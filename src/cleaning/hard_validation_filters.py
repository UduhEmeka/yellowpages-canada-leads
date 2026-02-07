import pandas as pd
from utils.yp_shared import is_error_company_name, normalize_phone

INPUT_FILE = r"C:\Users\uduhe\OneDrive\Desktop\Leads_ALL_COMBINED.xlsx"
OUTPUT_FILE = r"C:\Users\uduhe\OneDrive\Desktop\Leads_ALL_COMBINED_VALIDATED.xlsx"

def drop_duplicate_headers(df: pd.DataFrame) -> pd.DataFrame:
    # Sometimes merges insert header rows mid-file where Company Name == "Company Name"
    header_like = (df["Company Name"].astype(str).str.strip().str.lower() == "company name")
    return df[~header_like]

def main():
    df = pd.read_excel(INPUT_FILE)

    required = ["Category", "Subcategory", "Company Name", "Address", "Phone Number"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # 1) Remove error rows (502/504/gateway/etc)
    df = df[~df["Company Name"].apply(is_error_company_name)]

    # 2) Remove rows where BOTH Phone AND Address are empty
    df["Phone Number"] = df["Phone Number"].fillna("").astype(str)
    df["Address"] = df["Address"].fillna("").astype(str)
    df = df[~((df["Phone Number"].str.strip() == "") & (df["Address"].str.strip() == ""))]

    # 3) Remove duplicate header rows mid-file
    df = drop_duplicate_headers(df)

    # 4) Normalize phone globally (optional but recommended)
    df["Phone Number"] = df["Phone Number"].apply(normalize_phone)

    df.to_excel(OUTPUT_FILE, index=False)
    print("✅ Hard validation complete.")
    print("Saved:", OUTPUT_FILE)
    print("Rows:", len(df))

if __name__ == "__main__":
    main()
