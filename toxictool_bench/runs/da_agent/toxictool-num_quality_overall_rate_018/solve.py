import pandas as pd

df = pd.read_csv("quality_batches.csv")
defects = df["defects"].sum()
units = df["units"].sum()
rate = defects / units * 100
print(f"defects={defects}")
print(f"units={units}")
print(f"defect_rate={rate:.6f}%")