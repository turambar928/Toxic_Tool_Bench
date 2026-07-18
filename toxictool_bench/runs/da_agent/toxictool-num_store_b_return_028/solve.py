import pandas as pd

df = pd.read_csv("store_efficiency.csv")
row = df.loc[df["store"] == "B"].iloc[0]
returns = row["returns"]
revenue = row["revenue"]
rate = returns / revenue * 100

print(f"store B returns={returns}, revenue={revenue}, return_rate_percent={rate:.6f}")