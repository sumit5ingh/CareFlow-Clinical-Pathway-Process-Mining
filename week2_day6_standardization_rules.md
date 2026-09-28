
# CareFlow - Standardization Rules (Week 2, Day 6)

**Script:** `week_2_day4_standardize_export.py`
**Input:** `careflow_event_log.csv` (raw simulator output)
**Output:** `careflow_standardized.csv` (the file dbt and PM4Py should use)

## Columns

| Column | Type in output | Meaning |
|---|---|---|
| `Case_ID` | text/number | One patient's journey |
| `Activity_Name` | text | One of the 5 canonical activities |
| `Timestamp` | text, `YYYY-MM-DD HH:MM:SS` | When the activity happened |

## Rules applied (in this order)

**1. Activity names are mapped to 5 canonical names.**
Allowed values: `Registration`, `Triage`, `X-Ray`, `Doctor Consultation`, `Discharge`.
Before matching, each value is trimmed, lowercased, hyphens/underscores become spaces, extra spaces are collapsed and other special characters are removed. The result is then looked up in `VARIANT_MAP`.

| Raw value (examples) | Standardized |
|---|---|
| `regestration`, `Registration ` | Registration |
| `triaged`, `TRIAGE` | Triage |
| `xray`, `x ray`, `X_Ray` | X-Ray |
| `dr consultation`, `doctor consult`, `consultation` | Doctor Consultation |
| `discharged`, `Discharge` | Discharge |

A value that is not in the map is kept (only spaces cleaned) and a warning is printed. Fix: add a line to `VARIANT_MAP`.

**2. Timestamps use one format: `%Y-%m-%d %H:%M:%S`.**
Parsing is strict. A value in any other format becomes empty (NaT), a warning shows the count, and those rows sort to the end of the file.

**3. Exact duplicates are removed.**
Rows with the same `Case_ID` + `Activity_Name` + `Timestamp` count as one event (first kept). Repeated activities at *different* times (e.g. Triage / X-Ray loop-backs) are real events and are kept.

**4. Rows are sorted by `Case_ID`, then `Timestamp`.**
Stable sort: events with an identical timestamp keep their original order.

**5. Order is verified.**
The script checks that no case has an event earlier than the one before it, then prints a validation summary (rows, patients, canonical-only YES/NO, order OK YES/NO, columns).

## Before sharing the CSV

Read the validation summary. The file is saved even when a warning appears, so both "Canonical activities only" and "Timestamps in correct order" should say **YES**.

## Handoff to dbt (Member 3)

- dbt should load `careflow_standardized.csv` directly and **not** re-clean or re-standardize activity names or timestamps.
- Standardization is complete at this stage; dbt models should only build on top of it (e.g. staging, case-level metrics).
- Pending team confirmation (Day 5 review): shared GCP project ID, exact source file used in the BigQuery loads, and dbt consuming this file.
