import pandas as pd

df = pd.read_csv("quality_batches.csv")

# Try common column names for units
possible_cols = [c for c in df.columns if c.lower() in {"units", "unit", "quantity", "qty"}]
if not possible_cols:
    raise ValueError(f"No units-like column found. Columns: {list(df.columns)}")

col = possible_cols[0]
total_units = df[col].sum()

print(total_units)