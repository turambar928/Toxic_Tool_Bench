import pandas as pd

df = pd.read_csv("support_queue.csv")

print("COLUMNS:", df.columns.tolist())
print("HEAD:")
print(df.head().to_string(index=False))

time_col = None
for col in df.columns:
    if "minute" in col.lower():
        time_col = col
        break

if time_col is None:
    raise KeyError("No minutes-like column found")

result = (
    df.groupby("team", as_index=False)[time_col]
      .mean()
      .rename(columns={time_col: "avg_minutes"})
      .sort_values(["avg_minutes", "team"], ascending=[True, True])
)

print("\nTEAM_AVERAGES:")
print(result.to_string(index=False))

min_row = result.iloc[0]
print(f"\nLOWEST_TEAM={min_row['team']}")
print(f"LOWEST_AVG_MINUTES={min_row['avg_minutes']}")