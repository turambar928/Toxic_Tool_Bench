import pandas as pd

df = pd.read_csv("campaign_roi.csv")
avg_leads = df["leads"].mean()
print(avg_leads)