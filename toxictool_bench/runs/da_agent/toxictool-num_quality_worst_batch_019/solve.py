import pandas as pd

df = pd.read_csv("quality_batches.csv")

# Columns are: batch, line, units, defects
if not {"batch", "units", "defects"}.issubset(df.columns):
    raise ValueError(f"Unexpected columns: {list(df.columns)}")

# Defect rate = defects / units * 100
df["defect_rate"] = df["defects"] / df["units"] * 100

result = df.groupby("batch", dropna=False)["defect_rate"].mean().sort_values(ascending=False)

top_batch = result.index[0]
top_rate = result.iloc[0]

print(f"Top batch: {top_batch}")
print(f"Defect rate: {top_rate:.2f}%")