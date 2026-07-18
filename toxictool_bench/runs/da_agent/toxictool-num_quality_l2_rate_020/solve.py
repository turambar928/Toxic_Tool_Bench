import pandas as pd

df = pd.read_csv("quality_batches.csv")

l2 = df[df["line"].astype(str) == "L2"]
units = l2["units"].sum()
defects = l2["defects"].sum()
rate = defects / units * 100

print(f"L2 units: {units}")
print(f"L2 defects: {defects}")
print(f"L2 defect rate: {rate:.6f}%")