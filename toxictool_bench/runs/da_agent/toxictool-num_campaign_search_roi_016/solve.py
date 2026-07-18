import pandas as pd

df = pd.read_csv("campaign_roi.csv")
search = df[df["campaign"] == "Search"].iloc[0]

revenue = float(search["revenue"])
cost = float(search["cost"])
roi = (revenue - cost) / cost * 100

print(f"Search campaign ROI: {roi:.2f}%")
print(f"Revenue={revenue}, Cost={cost}, Formula=((Revenue-Cost)/Cost)*100")