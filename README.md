# YellowPages Canada Lead Automation Pipeline

A business automation and data collection pipeline built to support outbound sales and marketing campaigns using YellowPages Canada business listings.

This project automates what was originally a fully manual lead-collection task and transforms it into a structured, repeatable, and auditable data pipeline.

---

## Business Context

This project was developed in a real business setting at **Drake International** to support sales teams preparing for cold-outreach and marketing campaigns.

The original task required manually collecting **100 business leads per day** from YellowPages Canada, including:
- Company name
- Address
- Phone number
- Business category and subcategory

The automation introduced here reduces manual effort, improves data consistency, and enables faster lead delivery at scale.

---

## What This Project Does

The pipeline performs the following steps:

1. **Automated Data Collection**
   - Scrapes YellowPages Canada business listings by category and subcategory
   - Handles pagination, retries, and site instability
   - Extracts company name, address, phone number, category, and subcategory

2. **Data Cleaning & Validation**
   - Removes error pages and invalid listings (e.g. 502 / 504 / gateway errors)
   - Normalizes phone numbers into a consistent format
   - Removes rows with missing critical fields
   - Deduplicates records using phone number, name, and address logic

3. **Category Recovery & Merging**
   - Re-scrapes problematic or incomplete categories independently
   - Replaces specific categories in the master dataset without re-running the full pipeline
   - Safely merges clean category data back into the master file

4. **Sampling for Review & Demonstration**
   - Generates balanced sample datasets
   - Ensures fair representation across subcategories for demos or audits

---

## Project Structure

yellowpages-canada-leads/
│
├── data/
│ ├── final/ # Final cleaned lead datasets
│ └── samples/ # Balanced sample files for review/demo
│
├── src/
│ ├── scraping/ # Web scraping and recovery scripts
│ ├── cleaning/ # Validation, normalization, and filtering
│ ├── merging/ # Category replacement and master merges
│ └── utils/ # Shared helper functions
│
├── requirements.txt
└── README.md

---

## Technologies Used

- **Python** — core automation and data processing
- **BeautifulSoup & Selenium** — web scraping and navigation
- **Excel (openpyxl)** — business-friendly output and delivery
- **GitHub** — version control and project documentation

---

## Results & Impact

- Successfully collected and cleaned **4,465 business leads**
- Covered multiple industries including:
  - Business & Professional Services
  - Food & Beverages
  - Health & Medicine
  - Automotive
  - Transportation
- Reduced a fully manual process into a repeatable automated workflow
- Produced sales-ready Excel files suitable for immediate outreach

---

## How to Run (High Level)

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Run a category scrape:

python src/scraping/recovery_category_scraper.py

3. Clean and validate data:

python src/cleaning/hard_validation_filters.py

4. Merge cleaned data into the master dataset:

python src/merging/replace_category_in_master_and_merge_FAST.py
