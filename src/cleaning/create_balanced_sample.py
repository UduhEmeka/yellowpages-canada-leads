import pandas as pd

INPUT_FILE = r"C:\Users\uduhe\OneDrive\Desktop\Leads_ALL_COMBINED_VALIDATED.xlsx"
OUTPUT_FILE = r"C:\Users\uduhe\OneDrive\Desktop\leads_sample_balanced.xlsx"

ROWS_PER_SUBCATEGORY = 5
RANDOM_SEED = 42

def main():
    df = pd.read_excel(INPUT_FILE)

    if "Subcategory" not in df.columns:
        raise ValueError("❌ Column 'Subcategory' not found in dataset")

    parts = []
    for subcat, group in df.groupby("Subcategory", dropna=False):
        if len(group) <= ROWS_PER_SUBCATEGORY:
            parts.append(group)
        else:
            parts.append(group.sample(n=ROWS_PER_SUBCATEGORY, random_state=RANDOM_SEED))

    out = pd.concat(parts, ignore_index=True)
    out.to_excel(OUTPUT_FILE, index=False)

    print("✅ Balanced sample created")
    print("Subcategories represented:", out["Subcategory"].nunique())
    print("Rows in sample:", len(out))
    print("Saved:", OUTPUT_FILE)

if __name__ == "__main__":
    main()
