import pandas as pd

df = pd.read_csv("subscription_cohorts.csv")
jan = df[df["cohort"].astype(str).str.strip().str.lower() == "jan"].copy()

if jan.empty:
    raise ValueError("No Jan cohort found")

row = jan.iloc[0]
users_start = float(row["users_start"])
users_end = float(row["users_end"])
churn_pct = (users_start - users_end) / users_start * 100

print(f"Jan cohort: users_start={users_start:g}, users_end={users_end:g}, churn_pct={churn_pct:.2f}%")