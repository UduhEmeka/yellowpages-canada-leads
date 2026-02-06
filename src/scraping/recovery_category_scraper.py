import re
import time
from typing import List, Dict, Tuple, Optional

import pandas as pd
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from src.utils.yp_shared import (
    CategoryJob,
    fetch_html,
    soup,
    unique_keep_order,
    normalize_phone,
    is_error_company_name,
)

# -----------------------------
# SETTINGS
# -----------------------------
OUTPUT_FILE = r"C:\Users\uduhe\Desktop\YP_OUTPUT\TRANSPORTATION_RECOVERED_CLEAN.xlsx"

# For stability: don’t hammer the site
SLEEP_BETWEEN_PAGES = 0.8
SLEEP_BETWEEN_PROFILES = 0.5

MAX_PROFILES_PER_SEARCH_TERM = None  # set e.g. 200 if you want to cap
HEADLESS = True


# -----------------------------
# Selenium setup (fallback + profile pages)
# -----------------------------
def make_driver() -> webdriver.Chrome:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(45)
    return driver


# -----------------------------------
# Extract search URLs from level-2 page
# -----------------------------------
def extract_search_links_from_level2_html(level2_html: str) -> List[str]:
    s = soup(level2_html)

    # YellowPages level-2 pages often contain links to leaf terms (level-3),
    # which lead to search pages like /search/si/1/<TERM>/<CITY>
    search_links = []

    for a in s.select("a[href]"):
        href = a.get("href", "").strip()
        if not href:
            continue

        # keep search links only
        if href.startswith("/search/si/"):
            search_links.append("https://www.yellowpages.ca" + href)

    return unique_keep_order(search_links)


def discover_search_links(job: CategoryJob, driver: webdriver.Chrome) -> List[str]:
    try:
        html = fetch_html(job.level2_url)
        links = extract_search_links_from_level2_html(html)
        if links:
            return links
        # If fetch succeeds but no links found, fallback to base search
    except Exception as e:
        print(f"    ! urllib fetch failed for level-2 page: {e}")
        print("    -> Falling back to Selenium page_source for discovery...")

        driver.get(job.level2_url)
        time.sleep(2.0)
        html = driver.page_source
        links = extract_search_links_from_level2_html(html)
        if links:
            return links

    # last resort: build one base search using the level-2 subcategory name
    base = f"https://www.yellowpages.ca/search/si/1/{quote_plus_safe(job.subcategory)}/{job.city_query.replace('+', '%20')}"
    base = base.replace("%20", "+")
    return [base]


def quote_plus_safe(text: str) -> str:
    # similar to urllib.parse.quote_plus but without importing extra
    return re.sub(r"\s+", "+", text.strip()).replace("&", "%26").replace("/", "%2F")


# -----------------------------------
# Parse search results for profile URLs
# -----------------------------------
def extract_profile_links_from_search_html(html: str) -> List[str]:
    s = soup(html)
    out = []

    # profile links are usually inside results cards; safest approach:
    # collect links that look like business profile pages (/biz/ or /bus/ etc)
    for a in s.select("a[href]"):
        href = a.get("href", "").strip()
        if not href:
            continue
        if href.startswith("/biz/") or href.startswith("/bus/") or "/site/" in href:
            if href.startswith("/"):
                href = "https://www.yellowpages.ca" + href
            out.append(href)

    return unique_keep_order(out)


def build_next_page_url(search_url: str, page_num: int) -> str:
    # YellowPages uses /search/si/<page>/<TERM>/<CITY>
    # so replace /si/1/ with /si/<page_num>/
    return re.sub(r"/search/si/\d+/", f"/search/si/{page_num}/", search_url)


# -----------------------------------
# Profile parsing: company, address, phone
# -----------------------------------
def parse_profile(html: str) -> Tuple[str, str, str]:
    s = soup(html)

    # Company name: common selectors
    name = ""
    for sel in ["h1", "h1[itemprop='name']", "h1.ml-0"]:
        tag = s.select_one(sel)
        if tag and tag.get_text(strip=True):
            name = tag.get_text(strip=True)
            break

    # Phone: try tel: links
    phone = ""
    tel = s.select_one("a[href^='tel:']")
    if tel:
        phone = tel.get("href", "").replace("tel:", "").strip()

    # Address: look for schema/address blocks
    address = ""
    addr = s.select_one("[itemprop='address']")
    if addr:
        address = addr.get_text(" ", strip=True)

    # fallback: search for an obvious address line
    if not address:
        possible = s.find(string=re.compile(r"\b(Ottawa|ON|Ontario|QC|Quebec)\b", re.I))
        if possible:
            address = " ".join(str(possible).split())

    return name.strip(), address.strip(), phone.strip()


# -----------------------------------
# Main scrape loop
# -----------------------------------
def scrape_job(job: CategoryJob, driver: webdriver.Chrome) -> List[Dict]:
    print(f"\n=== RECOVERING: {job.subcategory} ===")
    print(f"Level-2 URL: {job.level2_url}")

    search_links = discover_search_links(job, driver)
    print(f"Search links found (used for search only): {len(search_links)}")

    rows = []
    seen_profile_urls = set()

    for i, search_url in enumerate(search_links, start=1):
        print(f"  [{i}/{len(search_links)}] Base Search: {search_url}")

        added_this_term = 0

        for page in range(1, 999):  # stop when empty
            page_url = build_next_page_url(search_url, page)
            driver.get(page_url)
            time.sleep(1.4)

            page_html = driver.page_source
            profile_links = extract_profile_links_from_search_html(page_html)

            if not profile_links:
                print(f"    Page {page}: profiles found=0 (stop)")
                break

            new_links = [u for u in profile_links if u not in seen_profile_urls]
            print(f"    Page {page}: profiles found={len(profile_links)} new={len(new_links)}")

            for profile_url in new_links:
                if MAX_PROFILES_PER_SEARCH_TERM and added_this_term >= MAX_PROFILES_PER_SEARCH_TERM:
                    break

                seen_profile_urls.add(profile_url)

                try:
                    driver.get(profile_url)
                    time.sleep(1.2)
                    ph = driver.page_source

                    company, address, phone = parse_profile(ph)
                    phone = normalize_phone(phone)

                    # Hard drop obvious error pages
                    if is_error_company_name(company):
                        continue

                    # Keep only rows that have at least phone or address (basic quality)
                    if not phone and not address:
                        continue

                    rows.append({
                        "Category": job.category,
                        "Subcategory": job.subcategory,
                        "Company Name": company,
                        "Address": address,
                        "Phone Number": phone,
                    })
                    added_this_term += 1
                    time.sleep(SLEEP_BETWEEN_PROFILES)

                except Exception:
                    # if a profile fails, just skip it
                    continue

            time.sleep(SLEEP_BETWEEN_PAGES)

        print(f"    -> Total added from this search term: {added_this_term}")

    return rows


def run(jobs: List[CategoryJob], output_path: str):
    driver = make_driver()
    all_rows = []

    try:
        for job in jobs:
            all_rows.extend(scrape_job(job, driver))
    finally:
        driver.quit()

    df = pd.DataFrame(all_rows, columns=["Category", "Subcategory", "Company Name", "Address", "Phone Number"])

    # Final hard validation (global)
    df = df[~df["Company Name"].apply(is_error_company_name)]
    df = df[~((df["Phone Number"].fillna("") == "") & (df["Address"].fillna("") == ""))]

    df.to_excel(output_path, index=False)
    print(f"\nDONE. Total recovered leads: {len(df)}")
    print("Saved:", output_path)


if __name__ == "__main__":
    # ✅ Transportation (as requested)
    JOBS = [
        CategoryJob(category="Transportation", subcategory="Buses",
                    level2_url="https://www.yellowpages.ca/locations/Ontario/Ottawa/90020003.html"),
        CategoryJob(category="Transportation", subcategory="Mass & public transportation",
                    level2_url="https://www.yellowpages.ca/locations/Ontario/Ottawa/90020005.html"),
    ]

    run(JOBS, OUTPUT_FILE)
