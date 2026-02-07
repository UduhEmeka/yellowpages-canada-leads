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
```
yellowpages-canada-leads/
│
├── data/
│     ├── final/ # Final cleaned lead datasets
│     └── samples/ # Balanced sample files for review/demo
│
├── src/
│     ├── scraping/ # Web scraping and recovery scripts
│     ├── cleaning/ # Validation, normalization, and filtering
│     ├── merging/ # Category replacement and master merges
│     └── utils/ # Shared helper functions
│
├── requirements.txt
└── README.md
```

---

## Pipeline Architecture (How the System Works)

This project is organized as a modular data pipeline. Each stage performs a single responsibility and passes clean data to the next stage.

### 1. Scraping Layer
**Location:** `src/scraping/`

- Collects business listings from YellowPages Canada
- Navigates category and subcategory pages
- Handles pagination, retries, and unstable responses
- Outputs raw but structured lead data

### 2. Cleaning & Validation Layer
**Location:** `src/cleaning/`

- Removes invalid rows (error pages, empty listings)
- Standardizes phone number formats
- Filters incomplete records (missing phone and address)
- Ensures data quality before merging

### 3. Merging & Replacement Layer
**Location:** `src/merging/`

- Allows individual categories to be re-scraped independently
- Replaces only the affected category in the master dataset
- Prevents unnecessary full re-runs of the pipeline
- Deduplicates records during merge operations

### 4. Shared Utilities
**Location:** `src/utils/`

- Centralized helper functions used across the pipeline
- Reduces duplicated logic
- Ensures consistent behavior across scripts

### 5. Output Layer
**Location:** `data/`

- `data/final/` contains cleaned, sales-ready datasets
- `data/samples/` contains balanced samples for review or demos

This architecture makes the pipeline reusable, auditable, and easy to extend to new categories or locations.

---

## Technologies Used

- **Python** — core automation and data processing
- **BeautifulSoup & Selenium** — web scraping and navigation
- **Excel (openpyxl)** — business-friendly output and delivery
- **GitHub** — version control and project documentation

---

## Results & Impact

- Automated a previously manual lead-collection process that required producing **100 leads per day**
- Built a repeatable pipeline that collected, cleaned, and structured **4,465 sales-ready business leads**
- Covered multiple high-value industries, including:
  - Business & Professional Services
  - Food & Beverages
  - Health & Medicine
  - Automotive
  - Transportation
- Improved data quality by:
  - Removing invalid listings and server-error pages
  - Standardizing phone number formats
  - Eliminating duplicates across categories
- Reduced manual effort and turnaround time for sales preparation
- Delivered Excel-based outputs that could be immediately used by non-technical sales teams

This project demonstrates practical automation, data engineering fundamentals, and business-focused problem solving in a real operational context.

---

## How to Run This Project

This project is designed to be run as a modular pipeline. You can run individual steps independently depending on your needs.

### Prerequisites

- Python 3.10+
- Google Chrome (required for Selenium)
- Git installed

Install required Python packages:

   pip install -r requirements.txt


#Step 1: Scrape YellowPages Data

To scrape a category or recover a specific category:

   python src/scraping/recovery_category_scraper.py


This script:

- Navigates YellowPages category and subcategory pages

- Collects business name, address, phone number, and category metadata

- Handles pagination and temporary site errors

#Step 2: Clean and Validate Data

Run validation and normalization checks:

   python src/cleaning/hard_validation_filters.py


This step:

- Removes invalid or error listings

- Standardizes phone number formats

- Removes incomplete records

- Ensures the dataset is sales-ready

#Step 3: Merge or Replace Categories in the Master Dataset

To replace a single category in the master file without re-running the full pipeline:

   python src/merging/replace_category_in_master_and_merge_FAST.py


This allows:

- Targeted re-scraping of problematic categories

- Safe replacement without duplicating data

- Efficient updates to large datasets

Sample Data

A small, balanced sample dataset is included in:

   data/samples/leads_sample_100.xlsx

This file demonstrates the final structure and formatting of the cleaned output without exposing full production data.
