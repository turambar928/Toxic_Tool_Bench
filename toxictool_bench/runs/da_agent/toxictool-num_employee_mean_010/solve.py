import pandas as pd

df = pd.read_csv("employee_productivity.csv")
avg_tasks_completed = df["tasks_completed"].mean()
print(f"{avg_tasks_completed}")