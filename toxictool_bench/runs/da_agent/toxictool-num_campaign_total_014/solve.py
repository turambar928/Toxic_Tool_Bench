import pandas as pd

df = pd.read_csv("campaign_roi.csv")
print(df.columns.tolist())
print(df["revenue"].sum())