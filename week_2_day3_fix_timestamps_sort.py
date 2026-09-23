"""
CareFlow - Day 2, Day 3 - Timestamp Standardization + Sort + Dedup

"""

import pandas as pd

INPUT_FILE = "careflow_event_log_clean.csv"          # Day 2 output
OUTPUT_FILE = "careflow_event_log_clean_sorted.csv"   # Day 3 output

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse Timestamp into real datetimes. Anything that fails to
    parse becomes NaT so it's easy to spot and fix, instead of
    silently breaking the sort later."""
    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], format=TIMESTAMP_FORMAT, errors="coerce"
    )
    bad = df["Timestamp"].isna().sum()
    if bad:
        print(f"WARNING - {bad} row(s) had a Timestamp that could not be "
              f"parsed as '{TIMESTAMP_FORMAT}'. These will sort to the end.")
    else:
        print("All Timestamp values parsed cleanly.")
    return df


def drop_duplicate_events(df: pd.DataFrame) -> pd.DataFrame:
    """Same patient + same activity + same timestamp = the same event
    logged more than once. Keep the first occurrence, drop the rest."""
    before = len(df)
    df = df.drop_duplicates(subset=["Case_ID", "Activity_Name", "Timestamp"], keep="first")
    removed = before - len(df)
    print(f"Duplicate (Case_ID, Activity_Name, Timestamp) rows removed: {removed}")
    return df


def sort_by_case_and_time(df: pd.DataFrame) -> pd.DataFrame:
    """Sort so every case's events read in true time order - this is
    what makes the event log usable for process mining (PM4Py needs
    each trace ordered start to finish)."""
    df = df.sort_values(["Case_ID", "Timestamp"], kind="mergesort")
    df = df.reset_index(drop=True)
    return df


def check_still_out_of_order(df: pd.DataFrame) -> None:
    """Sanity check after sorting/deduping: confirm no case still has
    a timestamp that goes backwards relative to the previous event."""
    out_of_order = (
        df.groupby("Case_ID")["Timestamp"]
        .apply(lambda s: (s.diff().dropna() < pd.Timedelta(0)).any())
    )
    still_bad = out_of_order[out_of_order].index.tolist()
    if still_bad:
        print(f"WARNING - {len(still_bad)} case(s) still out of order after "
              f"fixing: {still_bad}")
    else:
        print("Confirmed: every case's events are now in correct time order.")


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} rows, {df['Case_ID'].nunique()} patients.\n")

    df = parse_timestamps(df)
    df = drop_duplicate_events(df)
    df = sort_by_case_and_time(df)
    check_still_out_of_order(df)

    # Write Timestamp back out in one consistent, readable string format
    df["Timestamp"] = df["Timestamp"].dt.strftime(TIMESTAMP_FORMAT)

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nFinal shape: {len(df)} rows, {df['Case_ID'].nunique()} patients.")
    print(f"Saved sorted, deduped file: {OUTPUT_FILE}")