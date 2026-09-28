# =====================================================================
# CareFlow - Week 2, Day 4 - Final Standardization Export
# =====================================================================
# PURPOSE
#   Takes the raw EHR event log produced by the simulator (Week 1) and
#   turns it into a clean, standardized event log that the next stages
#   (dbt, PM4Py process discovery) can consume without any more cleaning.
#
# INPUT   careflow_event_log.csv     (columns: Case_ID, Activity_Name, Timestamp)
# OUTPUT  careflow_standardized.csv  (same 3 columns, cleaned + sorted)
#
# WHAT THE SCRIPT DOES (in order)
#   1. Standardize Activity_Name  -> only the 5 canonical activity names remain
#   2. Parse Timestamp            -> real datetime values (bad ones flagged)
#   3. Remove duplicate events    -> same Case_ID + Activity + Timestamp
#   4. Sort by Case_ID, Timestamp -> each patient's journey is in time order
#   5. Verify order, print a validation summary, and save the CSV
#
# HOW TO RUN
#   python week_2_day4_standardize_export.py
#   (the input CSV must be in the same folder as this script)
#
# NOTE FOR DBT / DOWNSTREAM USERS
#   dbt should ingest careflow_standardized.csv as-is. Standardization is
#   already done here, so it should not be repeated in dbt.
# =====================================================================

import re
import pandas as pd

# --- File names --------------------------------------------------------
INPUT_FILE = "careflow_event_log.csv"          # raw event log (Day 1 input)
OUTPUT_FILE = "careflow_standardized.csv"       # final Day 4 deliverable

# --- Timestamp format --------------------------------------------------
# Used both to READ timestamps (strict parsing) and to WRITE them back out,
# so the input and output files use one identical format: 2024-01-31 14:05:09
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------
# Day 2 logic: Activity_Name standardization
# ---------------------------------------------------------------------
# Why: process mining treats "X-Ray" and "xray" as two different
# activities. If names are not identical, the process map gets extra
# fake steps and wrong counts.

# The only activity names allowed in the final file (the "official" list).
CANONICAL_ACTIVITIES = [
    "Registration",
    "Triage",
    "X-Ray",
    "Doctor Consultation",
    "Discharge",
]

# Lookup table: cleaned-up variant (lowercase, no punctuation) -> official name.
# Keys must already be in the form that normalize_key() produces, otherwise
# they will never match. To support a new variant, add a line here.
VARIANT_MAP = {
    "registration": "Registration",
    "regestration": "Registration",       # common typo
    "triage": "Triage",
    "triaged": "Triage",
    "xray": "X-Ray",
    "x ray": "X-Ray",                     # "X-Ray" / "x_ray" also land here
    "doctor consultation": "Doctor Consultation",
    "dr consultation": "Doctor Consultation",
    "doctor consult": "Doctor Consultation",
    "consultation": "Doctor Consultation",
    "discharge": "Discharge",
    "discharged": "Discharge",
}


def normalize_key(value: str) -> str:
    """Turn any spelling of an activity into a simple lookup key.

    Example: "  X-Ray " -> "x ray",  "Doctor_Consultation" -> "doctor consultation"

    Steps: trim spaces and lowercase, turn hyphens/underscores into spaces,
    squeeze repeated spaces into one, drop any other special characters.
    """
    value = value.strip().lower()
    value = re.sub(r"[\-_]+", " ", value)        # "x-ray", "x_ray" -> "x ray"
    value = re.sub(r"\s+", " ", value)           # many spaces -> one space
    value = re.sub(r"[^a-z0-9 ]", "", value)     # remove everything except letters/digits/space
    return value.strip()


def clean_activity_name(value: str) -> str:
    """Return the canonical activity name for one raw value.

    If the value is a known variant, return the official name from VARIANT_MAP.
    If it is unknown, return it with only the spacing cleaned (not silently
    "fixed"), so the check in the main block can warn that a VARIANT_MAP
    entry is needed.
    """
    key = normalize_key(str(value))
    if key in VARIANT_MAP:
        return VARIANT_MAP[key]
    # Unknown value: keep it, just collapse extra whitespace.
    return " ".join(value.split()).strip()


# ---------------------------------------------------------------------
# Day 3 logic: timestamp parsing, dedup, sort
# ---------------------------------------------------------------------

def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the Timestamp column from text to real datetime values.

    Parsing is strict (must match TIMESTAMP_FORMAT). Any value that does
    not match becomes NaT ("not a time") instead of crashing the script,
    and a warning shows how many rows were affected.
    """
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
    """Remove exact duplicate events.

    Two rows are duplicates when Case_ID, Activity_Name AND Timestamp are all
    the same (the same event recorded twice). The first one is kept.
    This runs AFTER activity standardization on purpose: "xray" and "X-Ray"
    at the same time are only recognised as duplicates once both say "X-Ray".
    A patient repeating an activity at a different time (e.g. a Triage
    loop-back) is NOT a duplicate and is kept.
    """
    before = len(df)
    df = df.drop_duplicates(subset=["Case_ID", "Activity_Name", "Timestamp"], keep="first")
    removed = before - len(df)
    print(f"Duplicate (Case_ID, Activity_Name, Timestamp) rows removed: {removed}")
    return df


def sort_by_case_and_time(df: pd.DataFrame) -> pd.DataFrame:
    """Sort so each patient's events sit together, oldest event first.

    kind="mergesort" is a stable sort: if two events of one patient share the
    same timestamp, they keep their original relative order.
    reset_index gives clean row numbers 0..n-1 after sorting.
    """
    df = df.sort_values(["Case_ID", "Timestamp"], kind="mergesort")
    df = df.reset_index(drop=True)
    return df


def check_still_out_of_order(df: pd.DataFrame) -> bool:
    """Sanity check: confirm no patient's events go backwards in time.

    For each Case_ID, s.diff() gives the time gap between consecutive events.
    A negative gap means an event happened before the previous one.
    Returns True if everything is in order, False (with a warning listing the
    bad Case_IDs) otherwise.
    """
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
    # Load the raw event log written by the simulator.
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} raw rows, {df['Case_ID'].nunique()} patients.\n")

    # Step 1: standardize activity names (Day 2)
    df["Activity_Name"] = df["Activity_Name"].apply(clean_activity_name)
    # Any name left that is not one of the 5 official ones means a new
    # spelling variant showed up; it needs a VARIANT_MAP entry.
    unexpected = sorted(set(df["Activity_Name"]) - set(CANONICAL_ACTIVITIES))
    if unexpected:
        print(f"WARNING - not in canonical list, needs a VARIANT_MAP entry: {unexpected}")
    else:
        print("All Activity_Name values match the 5 canonical activities.")

    # Step 2: fix timestamps, dedup, sort (Day 3)
    # Order matters: names first (so duplicates are detected correctly),
    # then timestamps parsed, then dedup, then sort.
    df = parse_timestamps(df)
    df = drop_duplicate_events(df)
    df = sort_by_case_and_time(df)
    order_ok = check_still_out_of_order(df)

    # Step 3: write Timestamp back out as a consistent, readable string
    # (datetime -> text in TIMESTAMP_FORMAT, so the CSV looks the same everywhere)
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

    # Save the final deliverable (index=False -> no extra row-number column).
    # NOTE: the file is written even if a warning appeared above, so always
    # read the validation summary before sharing the CSV.
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved final deliverable: {OUTPUT_FILE}")