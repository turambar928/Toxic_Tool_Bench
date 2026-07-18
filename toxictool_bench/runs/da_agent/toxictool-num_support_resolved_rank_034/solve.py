import pandas as pd

df = pd.read_csv("support_queue.csv")

print("COLUMNS:", list(df.columns))
for c in df.columns:
    print(f"\nCOLUMN: {c}")
    print(df[c].head(10).to_string(index=False))
    print("dtype:", df[c].dtype)