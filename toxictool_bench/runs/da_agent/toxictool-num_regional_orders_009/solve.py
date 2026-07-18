import pandas as pd

df = pd.read_csv("regional_sales.csv")

# Try common column names for number of orders
candidate_cols = ["orders", "order_count", "num_orders", "number_of_orders", "orders_count"]
col = None
for c in candidate_cols:
    if c in df.columns:
        col = c
        break

if col is None:
    raise ValueError(f"No orders column found. Available columns: {list(df.columns)}")

avg_orders = df[col].mean()
print(avg_orders)