import pandas as pd

df = pd.read_csv("store_efficiency.csv")
total_returns = df["returns"].sum()
total_revenue = df["revenue"].sum()
return_rate = (total_returns / total_revenue) * 100

print(f"total_returns={total_returns}")
print(f"total_revenue={total_revenue}")
print(f"return_rate_percentage={return_rate:.6f}")