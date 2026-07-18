import pandas as pd

df = pd.read_csv("subscription_cohorts.csv")
avg_users_end = df["users_end"].mean()
print(avg_users_end)