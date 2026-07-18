import pandas as pd

df = pd.read_csv("regional_sales.csv")

# Identify a likely sales column
candidate_cols = [c for c in df.columns if "sales" in c.lower() or "sale" in c.lower()]
if candidate_cols:
    sales_col = candidate_cols[0]
else:
    # Fall back to the first column with numeric values after coercion
    sales_col = None
    for c in df.columns:
        numeric = pd.to_numeric(df[c], errors="coerce")
        if numeric.notna().any():
            sales_col = c
            break
    if sales_col is None:
        raise ValueError("No numeric sales column found")

sales = pd.to_numeric(df[sales_col], errors="coerce")
avg_sales = sales.mean()

print(f"sales_col={sales_col}")
print(f"average_sales={avg_sales}")