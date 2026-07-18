import pandas as pd

df = pd.read_csv("subscription_cohorts.csv")

# Inspect columns to handle common cohort/retention layouts robustly
cols = [c.lower() for c in df.columns]
df.columns = cols

# Try to identify cohort and retention columns
cohort_col = None
retention_col = None

for c in df.columns:
    if "cohort" in c:
        cohort_col = c
    if "retention" in c:
        retention_col = c

if cohort_col is None or retention_col is None:
    # Fallback: assume first two columns are cohort and retention
    cohort_col = df.columns[0]
    retention_col = df.columns[1]

# Convert retention to numeric percentage if needed
ret = df[retention_col]
if ret.dtype == object:
    ret = ret.astype(str).str.replace("%", "", regex=False)
ret = pd.to_numeric(ret, errors="coerce")

result = df.assign(_retention=ret).dropna(subset=["_retention"])
idx = result["_retention"].idxmax()
top_cohort = result.loc[idx, cohort_col]
top_retention = result.loc[idx, "_retention"]

print(f"{top_cohort},{top_retention}")