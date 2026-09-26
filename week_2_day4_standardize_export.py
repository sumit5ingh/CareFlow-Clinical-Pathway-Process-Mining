
#CareFlow - Day 4 - Final Standardization Export



import re
import pandas as pd

INPUT_FILE = "careflow_event_log.csv"          # raw event log (Day 1 input)
OUTPUT_FILE = "careflow_standardized.csv"       # final Day 4 deliverable

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------
# Day 2 logic: Activity_Name standardization
# ---------------------------------------------------------------------

CANONICAL_ACTIVITIES = [
    "Registration",
    "Triage",
    "X-Ray",
    "Doctor Consultation",
    "Discharge",
]

VARIANT_MAP = {
    "registration": "Registration",
    "regestration": "Registration",       # common typo
    "triage": "Triage",
    "triaged": "Triage",
    "xray": "X-Ray",
    "x ray": "X-Ray",
    "doctor consultation": "Doctor Consultation",
    "dr consultation": "Doctor Consultation",
    "doctor consult": "Doctor Consultation",
    "consultation": "Doctor Consultation",
    "discharge": "Discharge",
    "discharged": "Discharge",
}


def normalize_key(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[\-_]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"[^a-z0-9 ]", "", value)
    return value.strip()


def clean_activity_name(value: str) -> str:
    key = normalize_key(str(value))
    if key in VARIANT_MAP:
        return VARIANT_MAP[key]
    return " ".join(value.split()).strip()


# ---------------------------------------------------------------------
# Day 3 logic: timestamp parsing, dedup, sort
# ---------------------------------------------------------------------

def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
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
    before = len(df)
    df = df.drop_duplicates(subset=["Case_ID", "Activity_Name", "Timestamp"], keep="first")
    removed = before - len(df)
    print(f"Duplicate (Case_ID, Activity_Name, Timestamp) rows removed: {removed}")
    return df


def sort_by_case_and_time(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["Case_ID", "Timestamp"], kind="mergesort")
    df = df.reset_index(drop=True)
    return df


def check_still_out_of_order(df: pd.DataFrame) -> bool:
    out_of_order = (
        df.groupby("Case_ID")["Timestamp"]
        .apply(lambda s: (s.diff().dropna() < pd.Timedelta(0)).any())
    )
    still_bad = out_of_order[out_of_order].index.tolist()
    if still_bad:
        print(f"WARNING - {len(still_bad)} case(s) still out of order: {still_bad}")
        return False
    print("Confirmed: every case's events are in correct time order.")
    return True


# ---------------------------------------------------------------------
# Day 4: run everything, validate, export final deliverable
# ---------------------------------------------------------------------

if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} raw rows, {df['Case_ID'].nunique()} patients.\n")

    # Step 1: standardize activity names (Day 2)
    df["Activity_Name"] = df["Activity_Name"].apply(clean_activity_name)
    unexpected = sorted(set(df["Activity_Name"]) - set(CANONICAL_ACTIVITIES))
    if unexpected:
        print(f"WARNING - not in canonical list, needs a VARIANT_MAP entry: {unexpected}")
    else:
        print("All Activity_Name values match the 5 canonical activities.")

    # Step 2: fix timestamps, dedup, sort (Day 3)
    df = parse_timestamps(df)
    df = drop_duplicate_events(df)
    df = sort_by_case_and_time(df)
    order_ok = check_still_out_of_order(df)

    # Step 3: write Timestamp back out as a consistent, readable string
    df["Timestamp"] = df["Timestamp"].dt.strftime(TIMESTAMP_FORMAT)

    # Step 4: final validation summary (useful for Day 6 doc too)
    print("\n" + "=" * 60)
    print("FINAL VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Rows: {len(df)}")
    print(f"Patients (Case_ID): {df['Case_ID'].nunique()}")
    print(f"Canonical activities only: {'YES' if not unexpected else 'NO - see warning above'}")
    print(f"Timestamps in correct order: {'YES' if order_ok else 'NO - see warning above'}")
    print(f"Columns: {list(df.columns)}")

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved final deliverable: {OUTPUT_FILE}")