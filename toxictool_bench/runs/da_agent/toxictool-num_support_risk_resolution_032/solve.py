import pandas as pd

df = pd.read_csv("support_queue.csv")

risk = df[df["team"].astype(str).str.strip().eq("Risk")]
if risk.empty:
    raise SystemExit("Risk team row not found")

row = risk.iloc[0]
tickets = float(row["tickets"])
resolved = float(row["resolved"])
rate = resolved / tickets * 100 if tickets else 0.0

print(f"Risk team resolved: {resolved:g}")
print(f"Risk team tickets: {tickets:g}")
print(f"Risk team resolution rate: {rate:.2f}%")