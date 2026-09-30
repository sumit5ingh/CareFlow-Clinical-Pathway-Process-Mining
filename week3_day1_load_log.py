import pandas as pd
import pm4py

FILE = "careflow_standardized.csv"   # file ka naam yahin badalna

# 1. CSV load karo
df = pd.read_csv(FILE)
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# 2. PM4Py ke format mein badlo
df = pm4py.format_dataframe(
    df,
    case_id="Case_ID",
    activity_key="Activity_Name",
    timestamp_key="Timestamp",
)
df = df.sort_values(["case:concept:name", "time:timestamp"])

# 3. Quick checks
print("Total cases:", df["case:concept:name"].nunique())
print("Total events:", len(df))
print("Activities:", df["concept:name"].unique())
print("Empty values:", df.isna().sum().sum())

# 4. Directly-follows graph ka data
dfg, start_acts, end_acts = pm4py.discover_dfg(df)
for (a, b), count in sorted(dfg.items(), key=lambda x: -x[1])[:10]:
    print(a, "->", b, ":", count)