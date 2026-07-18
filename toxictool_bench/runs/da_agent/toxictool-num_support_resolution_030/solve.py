import pandas as pd

df = pd.read_csv("support_queue.csv")

# Identify resolved tickets robustly
resolved_col = None
for col in df.columns:
    if col.lower() in {"resolved", "is_resolved", "resolution_status", "status"}:
        resolved_col = col
        break

if resolved_col is None:
    raise ValueError(f"No obvious resolution column found. Columns: {list(df.columns)}")

series = df[resolved_col]

if series.dtype == bool:
    resolved_count = int(series.sum())
elif pd.api.types.is_numeric_dtype(series):
    resolved_count = int((series == 1).sum())
else:
    s = series.astype(str).str.strip().str.lower()
    resolved_count = int(s.isin({"resolved", "true", "1", "yes", "y"}).sum())

total_tickets = len(df)
resolution_rate = resolved_count / total_tickets * 100

print(f"resolved_count={resolved_count}")
print(f"total_tickets={total_tickets}")
print(f"resolution_rate={resolution_rate:.6f}")