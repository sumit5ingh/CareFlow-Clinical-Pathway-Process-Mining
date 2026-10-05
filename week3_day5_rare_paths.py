import pandas as pd

LOG = "careflow_event_log_clean_sorted.csv"   # Day 1 jaisi hi file
THRESHOLD = 1.0                               # % cases se kam = rare

df = pd.read_csv(LOG, parse_dates=["Timestamp"])
df = df.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)
total_cases = df["Case_ID"].nunique()

# 1. Variants + rare variants
variants = (df.groupby("Case_ID")["Activity_Name"].apply(tuple)
              .value_counts().reset_index())
variants.columns = ["Variant", "Cases"]
variants["Pct_of_Total"] = (variants["Cases"] / total_cases * 100).round(2)
rare_var = variants[variants["Pct_of_Total"] < THRESHOLD].copy()

# 2. Transitions + rare transitions
df["Next_Activity"] = df.groupby("Case_ID")["Activity_Name"].shift(-1)
df["Next_Time"] = df.groupby("Case_ID")["Timestamp"].shift(-1)
pairs = df.dropna(subset=["Next_Activity"]).copy()
pairs["Gap_Hours"] = (pairs["Next_Time"] - pairs["Timestamp"]).dt.total_seconds() / 3600

trans = (pairs.groupby(["Activity_Name", "Next_Activity"])
              .agg(Cases=("Case_ID", "nunique"), Avg_Gap_Hrs=("Gap_Hours", "mean"))
              .reset_index()
              .rename(columns={"Activity_Name": "From", "Next_Activity": "To"}))
trans["Pct_of_Cases"] = (trans["Cases"] / total_cases * 100).round(2)
rare_tr = trans[trans["Pct_of_Cases"] < THRESHOLD].copy()

# 3. Anomaly checks (genuine exception vs data error)
count = {(r.From, r.To): r.Cases for r in trans.itertuples()}

def check(row):
    f, t = row["From"], row["To"]
    if f == t:
        return "Possible data error: duplicate event"
    if count.get((t, f), 0) > row["Cases"] * 3:
        return "Possible data error: reversed order"
    return "Likely genuine clinical exception - clinician se confirm karo"

rare_tr["Flag"] = rare_tr.apply(check, axis=1)
rare_tr["Avg_Gap_Hrs"] = rare_tr["Avg_Gap_Hrs"].round(2)

# same-timestamp / zero gap events
zero_gap = (pairs["Gap_Hours"] == 0).sum()

# 4. Variant-level flag: consecutive duplicate activity
rare_var["Has_Duplicate"] = rare_var["Variant"].apply(
    lambda v: any(a == b for a, b in zip(v, v[1:])))
rare_var["Variant"] = rare_var["Variant"].apply(" -> ".join)

# 5. Save: ek hi rare_paths.csv, Type column ke saath
out_tr = rare_tr.assign(Type="Transition",
                        Path=rare_tr["From"] + " -> " + rare_tr["To"])
out_var = rare_var.assign(Type="Variant", Path=rare_var["Variant"],
                          Flag=rare_var["Has_Duplicate"].map(
                              {True: "Possible data error: duplicate event",
                               False: "Review needed"}),
                          Pct_of_Cases=rare_var["Pct_of_Total"])
cols = ["Type", "Path", "Cases", "Pct_of_Cases", "Flag"]
pd.concat([out_tr[cols], out_var[cols]]).to_csv("rare_paths.csv", index=False)

print(f"Total cases: {total_cases}")
print(f"Rare variants (<{THRESHOLD}%): {len(rare_var)} of {len(variants)}")
print(f"Rare transitions (<{THRESHOLD}%): {len(rare_tr)} of {len(trans)}")
print(rare_tr["Flag"].value_counts().to_string())
print(f"Zero-gap transitions: {zero_gap}")
print("\nSaved: rare_paths.csv")