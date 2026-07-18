import pandas as pd

df = pd.read_csv("store_efficiency.csv")

# Try common column names for revenue and store identifiers
print("Columns:", list(df.columns))

revenue_col = None
store_col = None

for c in df.columns:
    cl = c.lower()
    if revenue_col is None and "revenue" in cl:
        revenue_col = c
    if store_col is None and ("store" in cl or "shop" in cl):
        store_col = c

if revenue_col is None:
    raise ValueError("Could not find a revenue column")

if store_col is not None:
    avg_revenue_per_store = df.groupby(store_col)[revenue_col].sum().mean()
else:
    # If each row already represents a store, use the revenue column mean directly
    avg_revenue_per_store = df[revenue_col].mean()

print(f"Average revenue per store: {avg_revenue_per_store}")