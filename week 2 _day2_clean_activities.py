"""
CareFlow - Day 2 - Activity Name Standardization
=================================================
Goal: clean Activity_Name so that spacing/case/spelling differences
don't create fake "different" activities downstream (PM4Py, dbt, Power BI
all group by exact string match).

"""

import re
import pandas as pd

INPUT_FILE = "careflow_event_log.csv"
OUTPUT_FILE = "careflow_event_log_clean.csv"

# Canonical activity names for this process.
CANONICAL_ACTIVITIES = [
    "Registration",
    "Triage",
    "X-Ray",
    "Doctor Consultation",
    "Discharge",
]

# Map any variant spelling/format -> canonical name.
# Keys are normalized (lowercase, punctuation-stripped) so this
# catches "xray", "x ray", "X_RAY", "x-ray " etc. all at once.
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
    """Turn a raw string into a lookup key: lowercase, strip, collapse
    spaces, drop punctuation so 'X-Ray', 'x_ray', 'X  Ray' all match."""
    value = value.strip().lower()
    value = re.sub(r"[\-_]+", " ", value)      # hyphens/underscores -> space
    value = re.sub(r"\s+", " ", value)          # collapse multiple spaces
    value = re.sub(r"[^a-z0-9 ]", "", value)    # drop stray punctuation
    return value.strip()


def clean_activity_name(value: str) -> str:
    key = normalize_key(str(value))
    if key in VARIANT_MAP:
        return VARIANT_MAP[key]
    # Unknown activity: at least return a tidy, title-cased version
    # instead of silently guessing, so it's easy to spot in the report.
    return " ".join(value.split()).strip()


def profile_activities(df: pd.DataFrame, label: str) -> pd.Series:
    counts = df["Activity_Name"].value_counts(dropna=False)
    print(f"--- {label}: {counts.shape[0]} unique Activity_Name values ---")
    print(counts.to_string())
    print()
    return counts


if __name__ == "__main__":
    df = pd.read_csv(INPUT_FILE)

    print(f"Loaded {len(df)} rows, {df['Case_ID'].nunique()} patients.\n")

    before_counts = profile_activities(df, "BEFORE cleaning")

    df["Activity_Name_Raw"] = df["Activity_Name"]  # keep original for the diff report
    df["Activity_Name"] = df["Activity_Name"].apply(clean_activity_name)

    after_counts = profile_activities(df, "AFTER cleaning")

    # Diff report: which raw values got remapped, and how many rows each affected
    changed = df[df["Activity_Name"] != df["Activity_Name_Raw"]]
    print(f"--- Rows changed: {len(changed)} ---")
    if len(changed) > 0:
        print(
            changed.groupby(["Activity_Name_Raw", "Activity_Name"])
            .size()
            .rename("row_count")
            .reset_index()
            .to_string(index=False)
        )
    else:
        print("No changes needed - Activity_Name was already clean and standardized.")
    print()

    # Flag anything that's still not one of the 5 canonical activities
    unexpected = sorted(set(df["Activity_Name"]) - set(CANONICAL_ACTIVITIES))
    if unexpected:
        print(f"WARNING - not in canonical list, needs a VARIANT_MAP entry: {unexpected}")
    else:
        print("All Activity_Name values now match the 5 canonical activities.")

    df = df.drop(columns=["Activity_Name_Raw"])
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved cleaned file: {OUTPUT_FILE}")