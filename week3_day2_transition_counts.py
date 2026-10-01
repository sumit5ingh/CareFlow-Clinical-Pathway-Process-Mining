import pandas as pd
import pm4py

# 1. Load log
df = pd.read_csv("careflow_event_log_clean_sorted.csv")

df = df.rename(columns={
    "Case_ID": "case:concept:name",
    "Activity_Name": "concept:name",
    "Timestamp": "time:timestamp",
})
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

# 2. Har case ke andar time ke hisaab se sort
df = df.sort_values(["case:concept:name", "time:timestamp"])

# 3. Har event ki next activity (sirf usi case ke andar)
df["Next_Activity"] = df.groupby("case:concept:name")["concept:name"].shift(-1)

# 4. Case ka last event: Next_Activity NaN hota hai, usse hata do
pairs = df.dropna(subset=["Next_Activity"])

# 5. Transition counts
transitions = (
    pairs.groupby(["concept:name", "Next_Activity"])
    .size()
    .reset_index(name="Count")
    .rename(columns={"concept:name": "From", "Next_Activity": "To"})
    .sort_values("Count", ascending=False)
)
print(transitions.head(10))
print("Total transitions:", transitions["Count"].sum())

# 6. Verification: pm4py ke DFG se compare
event_log = pm4py.format_dataframe(
    df, case_id="case:concept:name",
    activity_key="concept:name", timestamp_key="time:timestamp",
)
dfg, _, _ = pm4py.discover_dfg(event_log)
mismatch = 0
for _, row in transitions.iterrows():
    if dfg.get((row["From"], row["To"])) != row["Count"]:
        mismatch += 1
print("Mismatches vs pm4py DFG:", mismatch)

# 7. Save
transitions.to_csv("transitions.csv", index=False)