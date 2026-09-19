# CareFlow – Week 1: Simulated EHR Event Log

Synthetic hospital emergency/outpatient visit data, built for process mining (PM4Py), BigQuery loading, dbt normalization and Power BI reporting in the later weeks of the CareFlow project.

**No real patient data is used. Everything is randomly generated.**

## Files

| File | What it is |
|---|---|
| `careflow_simulator.py` | The generator script (all settings are at the top of the file) |
| `careflow_event_log.csv` | The output dataset, ready to load |
| `README.md` | This document |

## What the dataset represents

Each row is **one activity starting for one patient**. A patient's visit (a "case") is the set of rows sharing the same `Case_ID`, ordered by time. This is the standard event log shape process mining tools expect.

### Columns

| Column | Type | Example | Notes |
|---|---|---|---|
| `Case_ID` | text | `P0001` | One per patient visit. Format `P` + 4 digits, `P0001` to `P2000` |
| `Activity_Name` | text | `Triage` | One of 5 activities (see below) |
| `Timestamp` | text | `2026-09-15 08:27:00` | Format `YYYY-MM-DD HH:MM:SS`. This is when the activity **started**. |

The file is sorted by `Case_ID`, then `Timestamp`. There are no missing values and no duplicate rows.

### Activities

`Registration`, `Triage`, `X-Ray`, `Doctor Consultation`, `Discharge`

## Size

| Measure | Value |
|---|---|
| Patients (cases) | 2,000 |
| Events (rows) | 11,410 |
| Date range | 2026-09-15 08:03 to 2026-09-23 19:47 |
| Events per patient | 5 (normal path) or 7 (with loop-back) |

Activity counts: Registration 2,000 · Doctor Consultation 2,000 · Discharge 2,000 · Triage 2,705 · X-Ray 2,705.

## The two path variants

Every patient follows one of exactly two paths:

| Path | Patients | Share |
|---|---|---|
| Registration → Triage → X-Ray → Doctor Consultation → Discharge | 1,295 | 64.8% |
| Registration → Triage → X-Ray → **Triage → X-Ray** → Doctor Consultation → Discharge | 705 | 35.2% |

## Inefficiencies built in on purpose

These are the problems the analysis in Weeks 2–4 should be able to discover.

1. **Rework loop (X-Ray → Triage).** Each patient has a 35% chance of being sent back to Triage after X-Ray (simulating missing paperwork or a re-check), and then must repeat X-Ray. Actual result in this file: 35.2%.
2. **Waiting time between activities.** A random 5–45 minute wait (average about 25) is added before every activity except the first. This creates queues and bottlenecks.
3. **Longer visits for looped patients.** Average time from Registration to the start of Discharge:
   - normal path: about 145 minutes
   - loop-back path: about 221 minutes (roughly 76 minutes longer)
   - all patients: about 172 minutes (range 72 to 314)

## How activity duration and waiting work

Each activity takes a random duration, then a random wait follows before the next one starts:

| Activity | Duration (minutes) |
|---|---|
| Registration | 2–5 |
| Triage | 5–15 |
| X-Ray | 10–20 |
| Doctor Consultation | 10–25 |
| Discharge | 2–5 |

The dataset only stores **start** times, so durations and waits are not separate columns. To measure them, take the difference between consecutive events in a case (that gap = duration of the previous activity + the wait before the next one).

## Things to know before you start Week 2

- **Start time only.** There is no end timestamp, so it is not possible to separate activity time from waiting time from this file alone.
- **`Timestamp` is text in the CSV.** Cast it to `TIMESTAMP` when loading to BigQuery or parsing in pandas.
- **No breaks or closing hours.** Patients arrive every 2–10 minutes around the clock in the simulation clock, and the visit times do not pause overnight. Time-of-day analysis will not show realistic daily patterns.
- **Only 5 activities and 2 paths.** No cancelled visits, no missing or out-of-order events and no data-quality errors have been injected. If Week 2 needs messy data to practice normalization on, the simulator would need extending.
- **Loop-backs are identifiable** by `Triage` appearing twice in the same case.
- **No extra attributes.** There are no columns for department, staff, resource or patient details.

## How to regenerate the data

```bash
pip install pandas
python careflow_simulator.py
```

The random seed is fixed (`SEED = 42`), so you get the identical file every time. To change the size, loop-back probability, wait times or durations, edit the configuration section at the top of `careflow_simulator.py`, and update the numbers in this README to match.
