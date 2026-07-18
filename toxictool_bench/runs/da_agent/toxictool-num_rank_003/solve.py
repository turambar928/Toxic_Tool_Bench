import pandas as pd

df = pd.read_csv('/workspace/ab_test.csv')

# Group by segment and sum visitors and conversions
grouped = df.groupby('segment').agg(
    total_visitors=('visitors', 'sum'),
    total_conversions=('conversions', 'sum')
).reset_index()

grouped['conversion_rate'] = grouped['total_conversions'] / grouped['total_visitors']

grouped_sorted = grouped.sort_values('conversion_rate', ascending=False)

print(grouped_sorted.to_string(index=False))
print()
top = grouped_sorted.iloc[0]
print(f"Highest conversion rate segment: {top['segment']}")
print(f"Conversion rate: {top['conversion_rate']:.4f} ({top['conversion_rate']*100:.2f}%)")
print(f"Total visitors: {int(top['total_visitors'])}, Total conversions: {int(top['total_conversions'])}")