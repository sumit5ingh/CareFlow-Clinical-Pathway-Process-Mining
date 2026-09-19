import pandas as pd
import random
from datetime import datetime, timedelta

# ---- Carried over from Day 1/2/4/5 ----
HAPPY_PATH = ["Registration", "Triage", "X-Ray", "Doctor Consultation", "Discharge"]

ACTIVITY_DURATIONS_MINUTES = {
    "Registration":        (2, 5),
    "Triage":              (5, 15),
    "X-Ray":               (10, 20),
    "Doctor Consultation": (10, 25),
    "Discharge":           (2, 5),
}

LOOP_BACK_RULE = {
    "after_activity": "X-Ray",
    "loop_back_to": "Triage",
    "probability": 0.35,
}

WAIT_TIME_MINUTES = (5, 45)

# ---- New for Day 6 ----
random.seed(42)                     # same data every run
NUM_PATIENTS = 2000                 # scaled up from 25
OUTPUT_FILE = "careflow_event_log.csv"
ARRIVAL_GAP_MINUTES = (2, 10)       # gap between one arrival and the next


def generate_patient_journey(patient_id, start_time):
    """Same logic as Day 5: happy path + loop-back + wait times."""
    events = []
    current_time = start_time
    activity_sequence = list(HAPPY_PATH)

    looped_back = False
    if random.random() < LOOP_BACK_RULE["probability"]:
        looped_back = True
        xray_index = activity_sequence.index(LOOP_BACK_RULE["after_activity"])
        activity_sequence = (
            activity_sequence[: xray_index + 1]
            + [LOOP_BACK_RULE["loop_back_to"], LOOP_BACK_RULE["after_activity"]]
            + activity_sequence[xray_index + 1:]
        )

    for i, activity in enumerate(activity_sequence):
        if i > 0:
            current_time += timedelta(minutes=random.randint(*WAIT_TIME_MINUTES))

        min_dur, max_dur = ACTIVITY_DURATIONS_MINUTES[activity]
        events.append({
            "Case_ID": patient_id,
            "Activity_Name": activity,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        })
        current_time += timedelta(minutes=random.randint(min_dur, max_dur))

    return events, looped_back


def generate_multiple_patients(num_patients):
    """
    Day 6 fix: arrival time is now CUMULATIVE.
    Old code used randint(2, 10) * i, which pushed later patients
    further and further away (bad when i goes up to 2000).
    """
    all_events = []
    loop_back_count = 0
    arrival_time = datetime(2026, 9, 15, 8, 0, 0)

    for i in range(1, num_patients + 1):
        patient_id = f"P{i:04d}"                       # P0001 ... P2000
        arrival_time += timedelta(minutes=random.randint(*ARRIVAL_GAP_MINUTES))

        patient_events, looped_back = generate_patient_journey(patient_id, arrival_time)
        all_events.extend(patient_events)
        if looped_back:
            loop_back_count += 1

    return all_events, loop_back_count


def sanity_check(df):
    """Automatic version of 'open the CSV and check a few journeys'."""
    df = df.copy()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    grouped = df.groupby("Case_ID")

    print("--- Sanity checks ---")
    print("Missing values:", int(df.isna().sum().sum()))
    print("Duplicate rows:", int(df.duplicated().sum()))
    print("Every case starts with Registration:", (grouped["Activity_Name"].first() == "Registration").all())
    print("Every case ends with Discharge:", (grouped["Activity_Name"].last() == "Discharge").all())
    print("Time always moves forward:", (grouped["Timestamp"].diff().dropna() > pd.Timedelta(0)).all())
    print()
    print("Path variants:")
    print(grouped["Activity_Name"].apply(lambda s: " > ".join(s)).value_counts().to_string())


if __name__ == "__main__":
    all_events, loop_back_count = generate_multiple_patients(NUM_PATIENTS)

    df = pd.DataFrame(all_events, columns=["Case_ID", "Activity_Name", "Timestamp"])

    # Sort by patient, then by time -> required by the brief
    df = df.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)

    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Saved: {OUTPUT_FILE}")
    print(f"Total patients: {df['Case_ID'].nunique()}")
    print(f"Total events:   {len(df)}")
    print(f"Loop-backs: {loop_back_count} ({loop_back_count / NUM_PATIENTS:.1%})")
    print()
    sanity_check(df)

    print()
    print("First 3 patient journeys (check these manually):")
    print(df[df["Case_ID"].isin(["P0001", "P0002", "P0003"])].to_string(index=False))