"""
CareFlow - Day 1 - Load & Profile the Event Log
================================================
Goal: before touching/cleaning anything, understand exactly what's in
the raw file - nulls, duplicates, what activities exist, and whether
the timestamp column is actually usable as a timestamp.

This is a read-only profiling pass. Nothing gets modified or saved here;
Day 2 (cleaning) builds on top of what this script finds.
"""

import pandas as pd

INPUT_FILE = "careflow_event_log.csv"


def profile_event_log(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("1. SHAPE & COLUMNS")
    print("=" * 60)
    print(f"Rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"Dtypes:\n{df.dtypes}")
    print()

    print("=" * 60)
    print("2. NULLS / MISSING VALUES")
    print("=" * 60)
    nulls = df.isna().sum()
    print(nulls.to_string())
    print(f"Total nulls: {int(nulls.sum())}")
    print()

    print("=" * 60)
    print("3. DUPLICATE ROWS")
    print("=" * 60)
    dupe_count = df.duplicated().sum()
    print(f"Fully duplicate rows: {dupe_count}")
    # Also check duplicate (Case_ID, Activity_Name, Timestamp) combos specifically,
    # since a full-row dupe check misses cases with an extra unnamed index column etc.
    key_dupes = df.duplicated(subset=["Case_ID", "Activity_Name", "Timestamp"]).sum()
    print(f"Duplicate (Case_ID, Activity_Name, Timestamp) combos: {key_dupes}")
    print()

    print("=" * 60)
    print("4. UNIQUE ACTIVITIES")
    print("=" * 60)
    activities = df["Activity_Name"].value_counts(dropna=False)
    print(f"{activities.shape[0]} unique Activity_Name values:")
    print(activities.to_string())
    print()

    print("=" * 60)
    print("5. CASE_ID")
    print("=" * 60)
    print(f"Unique Case_IDs (patients): {df['Case_ID'].nunique()}")
    print(f"Events per patient - min: {df.groupby('Case_ID').size().min()}, "
          f"max: {df.groupby('Case_ID').size().max()}")
    print()

    print("=" * 60)
    print("6. TIMESTAMP FORMAT")
    print("=" * 60)
    print(f"Current dtype: {df['Timestamp'].dtype}  (raw column is text, not yet parsed)")
    print("Sample raw values:")
    print(df["Timestamp"].head(3).to_string(index=False))

    parsed = pd.to_datetime(df["Timestamp"], format="%Y-%m-%d %H:%M:%S", errors="coerce")
    unparseable = parsed.isna().sum()
    print(f"\nRows that FAIL to parse as 'YYYY-MM-DD HH:MM:SS': {unparseable}")
    if unparseable == 0:
        print("-> Timestamp format is consistent across all rows.")
        print(f"-> Date range: {parsed.min()} to {parsed.max()}")
    else:
        print("-> Some rows don't match the expected format - inspect these before Day 2:")
        print(df.loc[parsed.isna(), "Timestamp"].unique())
    print()

    print("=" * 60)
    print("7. TIME ORDER WITHIN EACH CASE")
    print("=" * 60)
    df_sorted_check = df.copy()
    df_sorted_check["Timestamp_parsed"] = parsed
    out_of_order = (
        df_sorted_check.sort_values(["Case_ID", "Timestamp_parsed"])
        .groupby("Case_ID")["Timestamp_parsed"]
        .apply(lambda s: (s.diff().dropna() < pd.Timedelta(0)).any())
    )
    print(f"Cases where timestamps go backwards after sorting: {out_of_order.sum()}")
    print("(this checks the data's internal consistency, not the raw row order)")


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    profile_event_log(df)