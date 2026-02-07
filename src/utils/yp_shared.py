import re
import time
from dataclasses import dataclass
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from bs4 import BeautifulSoup


# -----------------------------
# HTTP fetch with retry/backoff
# -----------------------------
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0 Safari/537.36"
    ),
    "Accept-Language": "en-CA,en;q=0.9",
}

def fetch_html(url: str, timeout: int = 30, attempts: int = 4, backoff_base: float = 1.6) -> str:
    last_err = None
    for i in range(1, attempts + 1):
        try:
            req = Request(url, headers=DEFAULT_HEADERS)
            with urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", errors="replace")
        except (HTTPError, URLError, TimeoutError) as e:
            last_err = e
            sleep_s = backoff_base * i
            print(f"    ! fetch_html failed (attempt {i}/{attempts}) -> {e}. Sleeping {sleep_s:.1f}s")
            time.sleep(sleep_s)
    raise last_err


# -----------------------------------------
# Phone normalization to: 613-526-4036 style
# -----------------------------------------
def normalize_phone(phone: str) -> str:
    if phone is None:
        return ""
    digits = re.sub(r"\D", "", str(phone)).strip()
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return ""
    return f"{digits[0:3]}-{digits[3:6]}-{digits[6:10]}"


# -----------------------------------------
# Hard error row detection for company field
# -----------------------------------------
ERROR_PATTERNS = (
    "502", "504", "gateway", "internal server error", "bad gateway", "gateway time-out",
)

def is_error_company_name(name: str) -> bool:
    if not name:
        return False
    lowered = str(name).strip().lower()
    return any(p in lowered for p in ERROR_PATTERNS)


# -----------------------------
# Location / Search URL builder
# -----------------------------
@dataclass(frozen=True)
class CategoryJob:
    category: str              # Level-1 (e.g., "Transportation")
    subcategory: str           # Level-2 (e.g., "Buses")
    level2_url: str            # Level-2 location URL
    city_query: str = "Ottawa+ON"  # used in search urls if needed


def soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def unique_keep_order(items):
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
