import pandas as pd

df = pd.read_csv("store_efficiency.csv")

# Try to infer likely column names robustly
cols = {c.lower(): c for c in df.columns}

# Common possibilities
store_col = next((cols[c] for c in cols if "store" in c), df.columns[0])
revenue_col = next((cols[c] for c in cols if "revenue" in c or "sales" in c), None)
staff_col = next((cols[c] for c in cols if "staff" in c or "employee" in c or "employees" in c), None)

if revenue_col is None or staff_col is None:
    raise ValueError(f"Could not infer revenue/staff columns from: {list(df.columns)}")

df["revenue_per_staff"] = df[revenue_col] / df[staff_col]

top = df.loc[df["revenue_per_staff"].idxmax(), [store_col, "revenue_per_staff"]]
store = top[store_col]
value = top["revenue_per_staff"]

print(f"{store}\t{value}")