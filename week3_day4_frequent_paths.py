import pandas as pd
import pm4py

# 1. Load log (Day 2/3 jaisa hi)
df = pd.read_csv("careflow_event_log_clean_sorted.csv")
df = df.rename(columns={
    "Case_ID": "case:concept:name",
    "Activity_Name": "concept:name",
    "Timestamp": "time:timestamp",
})
df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
df = df.sort_values(["case:concept:name", "time:timestamp"])

event_log = pm4py.format_dataframe(
    df, case_id="case:concept:name",
    activity_key="concept:name", timestamp_key="time:timestamp",
)
total_cases = event_log["case:concept:name"].nunique()

# 2. Variants (unique patient journeys)
variants = pm4py.get_variants(event_log)   # {(act1, act2, ...): case_count}


def as_tuple(v):
    return tuple(v) if not isinstance(v, str) else tuple(v.split(","))


variant_rows = [(as_tuple(v), c) for v, c in variants.items()]
variant_rows.sort(key=lambda x: -x[1])

print("Total cases:", total_cases)
print("Unique variants:", len(variant_rows))
print("Sum of variant counts == total cases:",
      sum(c for _, c in variant_rows) == total_cases)

# 3. Top 10 variants
top = variant_rows[:10]
top_variants = pd.DataFrame({
    "Rank": range(1, len(top) + 1),
    "Variant": [" -> ".join(v) for v, _ in top],
    "Steps": [len(v) for v, _ in top],
    "Case_Count": [c for _, c in top],
    "Pct_of_Total": [round(c / total_cases * 100, 2) for _, c in top],
})
top_variants["Cumulative_Pct"] = top_variants["Pct_of_Total"].cumsum().round(2)
print("\nTop 10 variants:")
print(top_variants.to_string(index=False))

# 4. Transitions ranked (happy path)
df["Next_Activity"] = df.groupby("case:concept:name")["concept:name"].shift(-1)
pairs = df.dropna(subset=["Next_Activity"])

trans = (
    pairs.groupby(["concept:name", "Next_Activity"])
    .agg(Count=("Next_Activity", "size"),
         Cases=("case:concept:name", "nunique"))
    .reset_index()
    .rename(columns={"concept:name": "From", "Next_Activity": "To"})
    .sort_values("Count", ascending=False)
    .reset_index(drop=True)
)
total_transitions = trans["Count"].sum()
trans.insert(0, "Rank", trans.index + 1)
trans["Pct_of_Transitions"] = (trans["Count"] / total_transitions * 100).round(2)
trans["Pct_of_Cases"] = (trans["Cases"] / total_cases * 100).round(2)

# Happy path = transitions of the most common variant
happy = set(zip(top[0][0][:-1], top[0][0][1:]))
trans["On_Happy_Path"] = [
    (f, t) in happy for f, t in zip(trans["From"], trans["To"])
]
print("\nTop 10 transitions:")
print(trans.head(10).to_string(index=False))
print("\nHappy path:", " -> ".join(top[0][0]),
      f"({top[0][1]} cases, {top_variants.loc[0, 'Pct_of_Total']}%)")

# 5. Save (Member 2 ko share karne ke liye)
top_variants.to_csv("top_variants.csv", index=False)
trans.to_csv("top_transitions.csv", index=False)
print("\nSaved: top_variants.csv, top_transitions.csv")