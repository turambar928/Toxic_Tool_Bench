import pandas as pd

df = pd.read_csv("subscription_cohorts.csv")

total_start = df["users_start"].sum()
total_end = df["users_end"].sum()
retention = total_end / total_start * 100

print(f"total_users_start={total_start}")
print(f"total_users_end={total_end}")
print(f"overall_retention_percentage={retention:.6f}")