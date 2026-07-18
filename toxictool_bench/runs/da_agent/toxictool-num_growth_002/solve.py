import pandas as pd

df = pd.read_csv("monthly_revenue.csv")

print("Shape:", df.shape)
print("Columns:", df.columns.tolist())
print(df.head())
print(df.tail())

numeric_cols = df.select_dtypes(include='number').columns.tolist()
print("Numeric columns:", numeric_cols)

# Compute growth rate from first to last month
revenue_col = numeric_cols[0]
first_val = df[revenue_col].iloc[0]
last_val = df[revenue_col].iloc[-1]
growth_rate = (last_val - first_val) / first_val * 100

print(f"\nFirst month revenue: {first_val}")
print(f"Last month revenue: {last_val}")
print(f"Growth rate: {growth_rate:.2f}%")