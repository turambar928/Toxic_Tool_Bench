import pandas as pd

df = pd.read_csv("regional_sales.csv")

# Try common sales column names; fall back to the first numeric column if needed.
possible_cols = [c for c in df.columns if c.lower() in {"sales", "sale", "revenue", "amount", "total_sales"}]
if possible_cols:
    col = possible_cols[0]
else:
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if not numeric_cols:
        raise ValueError("No numeric column found to compute total sales.")
    col = numeric_cols[0]

total_sales = df[col].sum()
print(f"Column used: {col}")
print(f"Total sales: {total_sales}")