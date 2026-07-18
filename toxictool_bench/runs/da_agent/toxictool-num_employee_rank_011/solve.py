import pandas as pd

df = pd.read_csv("employee_productivity.csv")
print(df.columns.tolist())
print(df.to_string(index=False))