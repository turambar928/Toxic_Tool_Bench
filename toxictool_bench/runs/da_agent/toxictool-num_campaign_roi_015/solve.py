import pandas as pd

df = pd.read_csv("campaign_roi.csv")
df["roi"] = (df["revenue"] - df["cost"]) / df["cost"] * 100

best = df.loc[df["roi"].idxmax(), ["campaign", "roi"]]
print(f"{best['campaign']},{best['roi']:.6f}")