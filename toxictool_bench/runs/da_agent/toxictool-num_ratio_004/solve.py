import pandas as pd

df = pd.read_csv("customer_segments.csv")

# Try to identify likely columns for segment and spend per user
print("COLUMNS:", list(df.columns))
print(df.head().to_string(index=False))

# Common candidate names
segment_col = None
spend_col = None

for c in df.columns:
    cl = c.lower()
    if segment_col is None and "segment" in cl:
        segment_col = c
    if spend_col is None and ("spend" in cl or "avg" in cl or "average" in cl):
        spend_col = c

if segment_col is None or spend_col is None:
    raise ValueError(f"Could not identify columns. segment_col={segment_col}, spend_col={spend_col}")

result = (
    df.groupby(segment_col, as_index=False)[spend_col]
      .mean()
      .sort_values(spend_col, ascending=False)
)

top = result.iloc[0]
print("\nRESULT:")
print(f"{segment_col}={top[segment_col]}")
print(f"{spend_col}={top[spend_col]:.6f}")