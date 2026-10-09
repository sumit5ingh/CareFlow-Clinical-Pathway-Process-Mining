import pandas as pd

df = pd.read_csv("careflow_event_log_clean_sorted.csv")
print("Columns:", list(df.columns))  

CASE, ACT, TS = "Case_ID", "Activity_Name", "Timestamp"
df[TS] = pd.to_datetime(df[TS])
df = df.sort_values([CASE, TS])
df["pos"] = df.groupby(CASE).cumcount() + 1
n_cases = df[CASE].nunique()

summary = df.groupby(ACT).agg(
    Event_Count=(ACT, "size"),
    Case_Count=(CASE, "nunique"),
    Avg_Position=("pos", "mean"),
).reset_index()
summary["Pct_Cases"] = (summary["Case_Count"] / n_cases * 100).round(1)
summary["Avg_Position"] = summary["Avg_Position"].round(2)

first = df.groupby(CASE)[ACT].first().value_counts()
last = df.groupby(CASE)[ACT].last().value_counts()
summary["Times_First"] = summary[ACT].map(first).fillna(0).astype(int)
summary["Times_Last"] = summary[ACT].map(last).fillna(0).astype(int)

summary = summary.sort_values("Avg_Position")
summary.to_csv("activity_list.csv", index=False)

print(f"\nTotal cases: {n_cases}, unique activities: {len(summary)}\n")
print(summary.to_string(index=False))