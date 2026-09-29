"""
CareFlow - Week 2, Day 7 - Final Validation of careflow_standardized.csv
=========================================================================
PURPOSE
    Last check before the final push. Confirms that the standardized event
    log is safe for dbt / PM4Py to use as-is. This script is READ-ONLY:
    it never changes or saves any data.

INPUT   careflow_standardized.csv  (Case_ID, Activity_Name, Timestamp)

HOW TO RUN
    python week_2_day7_final_validation.py
    python week_2_day7_final_validation.py path/to/careflow_standardized.csv

RESULT
    Prints PASS / FAIL for every check and a final verdict.
    Exit code 0 = all checks passed, 1 = at least one check failed.
"""

import sys
import pandas as pd

# --- Settings ------------------------------------------------------------
INPUT_FILE = sys.argv[1] if len(sys.argv) > 1 else "careflow_standardized.csv"
TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
EXPECTED_COLUMNS = ["Case_ID", "Activity_Name", "Timestamp"]

CANONICAL_ACTIVITIES = {
    "Registration",
    "Triage",
    "X-Ray",
    "Doctor Consultation",
    "Discharge",
}

# Reference numbers from the Week 1 README and Sai Bhavana's BigQuery
# validation. If the simulator settings change, update these.
EXPECTED_ROWS = 11410
EXPECTED_PATIENTS = 2000

results = []  # list of (check name, passed?, detail)


def record(name, passed, detail=""):
    """Store one check result and print it right away."""
    results.append((name, bool(passed), detail))
    status = "PASS" if passed else "FAIL"
    line = f"[{status}] {name}"
    if detail:
        line += f"  ->  {detail}"
    print(line)


def run_checks(df):
    # 1. Columns must be exactly the 3 agreed ones, in this order
    record(
        "Columns are Case_ID, Activity_Name, Timestamp",
        list(df.columns) == EXPECTED_COLUMNS,
        f"found {list(df.columns)}",
    )
    if list(df.columns) != EXPECTED_COLUMNS:
        return  # the checks below need these columns

    # 2. No missing values
    nulls = int(df.isna().sum().sum())
    record("No missing values", nulls == 0, f"{nulls} null(s)")

    # 3. Row and patient counts match the reference numbers
    record("Row count matches reference", len(df) == EXPECTED_ROWS,
           f"{len(df)} rows (expected {EXPECTED_ROWS})")
    record("Patient count matches reference", df["Case_ID"].nunique() == EXPECTED_PATIENTS,
           f"{df['Case_ID'].nunique()} patients (expected {EXPECTED_PATIENTS})")

    # 4. Only the 5 canonical activities, no stray spaces
    found = set(df["Activity_Name"].dropna().unique())
    extra = sorted(found - CANONICAL_ACTIVITIES)
    record("Only the 5 canonical activities", not extra,
           f"unexpected: {extra}" if extra else "5/5 canonical")
    padded = int((df["Activity_Name"] != df["Activity_Name"].str.strip()).sum())
    record("No leading/trailing spaces in Activity_Name", padded == 0,
           f"{padded} row(s)")

    # 5. Timestamps: strict format, no unparseable values
    parsed = pd.to_datetime(df["Timestamp"], format=TIMESTAMP_FORMAT, errors="coerce")
    bad_ts = int(parsed.isna().sum())
    record(f"All timestamps match {TIMESTAMP_FORMAT}", bad_ts == 0,
           f"{bad_ts} unparseable")
    if bad_ts:
        return  # ordering checks below need valid datetimes

    work = df.copy()
    work["Timestamp"] = parsed

    # 6. No duplicate events
    dupes = int(work.duplicated(subset=EXPECTED_COLUMNS).sum())
    record("No duplicate (Case_ID, Activity_Name, Timestamp)", dupes == 0,
           f"{dupes} duplicate(s)")

    # 7. File is sorted by Case_ID then Timestamp
    expected_order = work.sort_values(["Case_ID", "Timestamp"], kind="mergesort")
    is_sorted = expected_order.index.equals(work.index)
    record("File is sorted by Case_ID, then Timestamp", is_sorted)

    # 8. Time never goes backwards inside a case
    grouped = work.groupby("Case_ID")
    backwards = grouped["Timestamp"].apply(
        lambda s: (s.diff().dropna() < pd.Timedelta(0)).any()
    )
    record("No case has time going backwards", not backwards.any(),
           f"{int(backwards.sum())} case(s)")

    # 9. Every journey starts with Registration and ends with Discharge
    starts_ok = (grouped["Activity_Name"].first() == "Registration").all()
    ends_ok = (grouped["Activity_Name"].last() == "Discharge").all()
    record("Every case starts with Registration", starts_ok)
    record("Every case ends with Discharge", ends_ok)

    # 10. Path variants (information only, not pass/fail)
    paths = grouped["Activity_Name"].apply(lambda s: " > ".join(s)).value_counts()
    total_cases = work["Case_ID"].nunique()
    print("\nPath variants found:")
    for path, count in paths.items():
        print(f"  {count:>5} cases ({count / total_cases:.1%})  {path}")

    print(f"\nDate range: {work['Timestamp'].min()}  to  {work['Timestamp'].max()}")


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)
    print(f"Validating: {INPUT_FILE}  ({len(df)} rows)\n")

    run_checks(df)

    failed = [r for r in results if not r[1]]
    print("\n" + "=" * 60)
    if failed:
        print(f"FINAL VERDICT: FAIL - {len(failed)} of {len(results)} checks failed")
        for name, _, detail in failed:
            print(f"  - {name} ({detail})")
        sys.exit(1)
    print(f"FINAL VERDICT: ALL {len(results)} CHECKS PASSED - safe to push")
    sys.exit(0)