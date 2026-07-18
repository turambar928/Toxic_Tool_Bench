import pandas as pd

df = pd.read_csv("regional_sales.csv")

# Identify likely columns
print("Columns:", list(df.columns))
print(df.head().to_string(index=False))

# Normalize column names for robust access
cols = {c.lower().strip(): c for c in df.columns}
region_col = cols.get("region")
sales_col = cols.get("sales")

if region_col is None or sales_col is None:
    raise KeyError(f"Required columns not found. Available columns: {list(df.columns)}")

totals = df.groupby(region_col, as_index=False)[sales_col].sum()
top = totals.sort_values(by=sales_col, ascending=False).iloc[0]

print("\nTotal sales by region:")
print(totals.sort_values(by=sales_col, ascending=False).to_string(index=False))
print(f"\nTop region: {top[region_col]}")
print(f"Top total sales: {top[sales_col]}")