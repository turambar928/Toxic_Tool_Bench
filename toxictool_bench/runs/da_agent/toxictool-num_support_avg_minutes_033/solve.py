import pandas as pd

df = pd.read_csv("support_queue.csv")
avg_value = df["avg_minutes"].mean()
print(f"{avg_value:.10f}")