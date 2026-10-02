import pandas as pd
import pm4py

# 1. Load log (Day 2 jaisa hi)
df = pd.read_csv("careflow_event_log_clean_sorted.csv")
df = df.rename(columns={
    "Case_ID": "case:concept:name",
    "Activity_Name": "concept:name",
    "Timestamp": "time:timestamp",
})
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
df = df.sort_values(["case:concept:name", "time:timestamp"])

# 2. Manual transition counts (Day 2 logic)
df["Next_Activity"] = df.groupby("case:concept:name")["concept:name"].shift(-1)
pairs = df.dropna(subset=["Next_Activity"])
manual = pairs.groupby(["concept:name", "Next_Activity"]).size().to_dict()

# 3. pm4py DFG
event_log = pm4py.format_dataframe(
    df, case_id="case:concept:name",
    activity_key="concept:name", timestamp_key="time:timestamp",
)
dfg, start_acts, end_acts = pm4py.discover_dfg(event_log)

# 4. Verification: dono direction mein compare
mismatch = 0
for pair, count in manual.items():
    if dfg.get(pair) != count:
        mismatch += 1
for pair, count in dfg.items():
    if manual.get(pair) != count:
        mismatch += 1
print("DFG edges (pm4py):", len(dfg), "| Manual edges:", len(manual))
print("Total transitions pm4py:", sum(dfg.values()),
      "| Manual:", sum(manual.values()))
print("Mismatches (manual vs pm4py):", mismatch)

# 5. Start aur end activities
print("\nStart activities:")
for act, cnt in sorted(start_acts.items(), key=lambda x: -x[1]):
    print(f"  {act}: {cnt}")
print("\nEnd activities:")
for act, cnt in sorted(end_acts.items(), key=lambda x: -x[1]):
    print(f"  {act}: {cnt}")

# Cross-check: manual first/last event per case
grp = df.groupby("case:concept:name")["concept:name"]
manual_start = grp.first().value_counts().to_dict()
manual_end = grp.last().value_counts().to_dict()
print("\nStart match:", manual_start == dict(start_acts))
print("End match:", manual_end == dict(end_acts))

# 6. DFG image save (Graphviz install hona chahiye)
pm4py.save_vis_dfg(dfg, start_acts, end_acts, "dfg_graph.png")
print("\nSaved: dfg_graph.png")

# 7. Start/end list file mein save
rows = (
    [("Start", a, c) for a, c in start_acts.items()]
    + [("End", a, c) for a, c in end_acts.items()]
)
pd.DataFrame(rows, columns=["Type", "Activity", "Cases"]).to_csv(
    "start_end_activities.csv", index=False
)
print("Saved: start_end_activities.csv")