import pandas as pd

df = pd.read_csv("toy_sales.csv")

avg_daily_sales = df["sales"].mean()
total_sales = df["sales"].sum()
num_days = len(df)

print(f"Number of days: {num_days}")
print(f"Total sales: {total_sales}")
print(f"Average daily sales: {avg_daily_sales:.4f}")