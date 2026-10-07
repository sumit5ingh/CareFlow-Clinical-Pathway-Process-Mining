"""
transition_analysis.py  -  CareFlow Week 3 (Member 1)
=====================================================
Week 3 Day 1-5  scripts with  single flow.

Input : careflow_event_log_clean_sorted.csv
        (columns: Case_ID, Activity_Name, Timestamp)
Output: transitions.csv, start_end_activities.csv, top_variants.csv,
        top_transitions.csv, rare_paths.csv, dfg_graph.png,
        findings_summary.md

Run   : python transition_analysis.py
"""

import pandas as pd

# ----------------------------------------------------------------------
# CONFIG - yahan se settings badlo
# ----------------------------------------------------------------------
INPUT_FILE = "careflow_event_log_clean_sorted.csv"
CASE, ACT, TS = "Case_ID", "Activity_Name", "Timestamp"
TOP_N = 5               # kitne top variants / transitions save karne hain
RARE_THRESHOLD = 0.01   # 1% se kam cases = rare


# ----------------------------------------------------------------------
# STEP 1 (Day 1): Load log
# ----------------------------------------------------------------------
def load_log(path):
    df = pd.read_csv(path)
    df[TS] = pd.to_datetime(df[TS])
    # sort zaroori hai: pehle patient (case), phir time
    df = df.sort_values([CASE, TS]).reset_index(drop=True)
    print(f"[1] Loaded {len(df)} events, {df[CASE].nunique()} cases")
    return df


# ----------------------------------------------------------------------
# STEP 2 (Day 2): Transition counts (A -> B)
# ----------------------------------------------------------------------
def build_transitions(df):
    df = df.copy()
    df["Next_Activity"] = df.groupby(CASE)[ACT].shift(-1)
    df["Next_Time"] = df.groupby(CASE)[TS].shift(-1)
    t = df.dropna(subset=["Next_Activity"]).copy()
    t["Gap_Minutes"] = (t["Next_Time"] - t[TS]).dt.total_seconds() / 60
    t = t.rename(columns={ACT: "From", "Next_Activity": "To"})

    counts = (t.groupby(["From", "To"])
                .agg(Count=(CASE, "size"), Cases=(CASE, "nunique"),
                     Avg_Gap_Min=("Gap_Minutes", "mean"))
                .reset_index()
                .sort_values("Count", ascending=False))
    counts.to_csv("transitions.csv", index=False)
    print(f"[2] {len(counts)} unique transitions -> transitions.csv")
    return t, counts


# ----------------------------------------------------------------------
# STEP 3 (Day 3): DFG + start/end activities
# ----------------------------------------------------------------------
def save_start_end(df):
    first = df.groupby(CASE)[ACT].first().value_counts().rename("Start_Count")
    last = df.groupby(CASE)[ACT].last().value_counts().rename("End_Count")
    se = pd.concat([first, last], axis=1).fillna(0).astype(int)
    se.index.name = "Activity"
    se.reset_index().to_csv("start_end_activities.csv", index=False)
    print("[3] start/end activities -> start_end_activities.csv")


def save_dfg_graph(counts):
    """DFG picture. Graphviz/pm4py na ho to skip ho jata hai."""
    try:
        from pm4py.visualization.dfg import visualizer as dfg_vis
        dfg = {(r.From, r.To): int(r.Count) for r in counts.itertuples()}
        gviz = dfg_vis.apply(dfg, variant=dfg_vis.Variants.FREQUENCY)
        dfg_vis.save(gviz, "dfg_graph.png")
        print("[3] DFG -> dfg_graph.png")
    except Exception as e:
        print(f"[3] DFG graph skipped ({e})")


# ----------------------------------------------------------------------
# STEP 4 (Day 4): Variants + frequent paths
# ----------------------------------------------------------------------
def build_variants(df):
    var = (df.groupby(CASE)[ACT].apply(lambda s: " -> ".join(s))
             .value_counts().rename_axis("Variant")
             .reset_index(name="Cases"))
    var["Percent"] = (var["Cases"] / var["Cases"].sum() * 100).round(2)
    var.head(TOP_N).to_csv("top_variants.csv", index=False)
    print(f"[4] {len(var)} variants; top {TOP_N} -> top_variants.csv")
    return var


def save_top_transitions(counts):
    counts.head(TOP_N).to_csv("top_transitions.csv", index=False)


# ----------------------------------------------------------------------
# STEP 5 (Day 5): Rare paths + anomaly flags
# ----------------------------------------------------------------------
def find_rare(var, counts, n_cases):
    cutoff = RARE_THRESHOLD * n_cases
    rare_var = var[var["Cases"] < cutoff].assign(Type="variant")
    rare_tr = counts[counts["Cases"] < cutoff].assign(Type="transition")
    rare = pd.concat([
        rare_var.rename(columns={"Variant": "Path"})[["Type", "Path", "Cases"]],
        rare_tr.assign(Path=rare_tr["From"] + " -> " + rare_tr["To"])
               [["Type", "Path", "Cases"]],
    ])
    rare.to_csv("rare_paths.csv", index=False)
    print(f"[5] rare: {len(rare_var)} variants, {len(rare_tr)} transitions"
          " -> rare_paths.csv")
    return rare_var, rare_tr


def data_error_checks(df, t):
    """Probable data errors: duplicate events, zero gap, reversed time."""
    dup = int((t["From"] == t["To"]).sum())      # same activity back-to-back
    zero = int((t["Gap_Minutes"] == 0).sum())    # timestamp same
    rev = int((t["Gap_Minutes"] < 0).sum())      # time ulta (sort ke baad 0 hona chahiye)
    print(f"[5] consecutive duplicates={dup}, zero-gap={zero}, reversed={rev}")
    return dup, zero, rev


# ----------------------------------------------------------------------
# STEP 6 (Day 6): Findings summary
# ----------------------------------------------------------------------
def write_summary(n_cases, var, counts, rare_var, rare_tr, errs):
    dup, zero, rev = errs
    lines = ["# CareFlow Week 3 - Findings Summary", "",
             f"Total cases: **{n_cases}** | Variants: **{len(var)}** | "
             f"Transitions: **{len(counts)}**", "",
             "## Top 3 frequent paths"]
    for i, r in enumerate(var.head(3).itertuples(), 1):
        lines.append(f"{i}. {r.Variant}  ({r.Cases} cases, {r.Percent}%)")
    lines += ["", "## Rare paths (<1% of cases)",
              f"- {len(rare_var)} rare variants, {len(rare_tr)} rare transitions "
              "(see rare_paths.csv)",
              "- Rework loops (e.g. X-Ray -> Triage) are by design of the "
              "simulation, but need clinician validation.", "",
              "## Unexpected transitions / data-quality flags",
              f"- Consecutive duplicate events: {dup}",
              f"- Zero time-gap transitions: {zero}",
              f"- Reversed-time transitions: {rev}",
              "- [Apne observations yahan add karo]"]
    with open("findings_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("[6] findings_summary.md written")


# ----------------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------------
def main():
    df = load_log(INPUT_FILE)
    n_cases = df[CASE].nunique()

    t, counts = build_transitions(df)
    save_start_end(df)
    save_dfg_graph(counts)

    var = build_variants(df)
    save_top_transitions(counts)

    rare_var, rare_tr = find_rare(var, counts, n_cases)
    errs = data_error_checks(df, t)

    write_summary(n_cases, var, counts, rare_var, rare_tr, errs)
    print("Done.")


if __name__ == "__main__":
    main()