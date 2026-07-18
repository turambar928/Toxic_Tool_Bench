# Average Daily Sales Report

## Result

**Average Daily Sales: 32.0**

## How It Was Computed

- Dataset: `toy_sales.csv` with columns `day` and `sales`
- Number of days: 10
- Total sales: 160
- Calculation: 160 ÷ 10 = **32.0**

The average was computed using `pandas` — specifically `df["sales"].mean()` — which sums all sales values and divides by the count of rows (days).