import pandas as pd

df = pd.read_csv("regional_sales.csv")
print(df.head())
print(df.columns)
print(df[df.astype(str).apply(lambda col: col.str.contains("West", case=False, na=False)).any(axis=1)].head(10))