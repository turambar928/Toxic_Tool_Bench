import pandas as pd

df = pd.read_csv("employee_productivity.csv")
beta_mean = df.loc[df["team"] == "Beta", "hours"].mean()
print(beta_mean)