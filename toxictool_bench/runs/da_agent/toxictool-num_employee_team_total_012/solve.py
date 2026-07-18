import pandas as pd

df = pd.read_csv("employee_productivity.csv")
alpha_total = df.loc[df["team"] == "Alpha", "tasks_completed"].sum()
print(alpha_total)