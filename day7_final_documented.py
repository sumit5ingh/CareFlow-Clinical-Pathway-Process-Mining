"""
CareFlow - Week 1 - EHR Data Simulator (Member 1)
==================================================
Generates a synthetic hospital-visit event log for process mining.

Each row = one activity STARTING for one patient:
    Case_ID | Activity_Name | Timestamp

What is built in on purpose (the "inefficiencies" for Week 2/3 to find):
    1. Happy path:  Registration -> Triage -> X-Ray -> Doctor Consultation -> Discharge
    2. Loop-back:   ~35% of patients are bounced from X-Ray back to Triage,
                    then repeat X-Ray before seeing the doctor.
    3. Wait times:  5-45 minutes of idle time between every pair of activities.

Run:  python careflow_simulator.py
Output: careflow_event_log.csv  (in the same folder)
"""

import random
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# 1. CONFIGURATION - change numbers here, not deep inside the functions
# ---------------------------------------------------------------------------

SEED = 42                      # fixed seed -> same dataset every run (reproducible for teammates)
NUM_PATIENTS = 2000            # dataset size ("a few thousand" per the brief)
OUTPUT_FILE = "careflow_event_log.csv"

# Simulation clock starts here; the first patient arrives shortly after.
START_TIME = datetime(2026, 9, 15, 8, 0, 0)

# Gap between one patient's arrival and the next patient's arrival (minutes).
ARRIVAL_GAP_MINUTES = (2, 10)

# The ideal, no-problems route through the hospital.
HAPPY_PATH = ["Registration", "Triage", "X-Ray", "Doctor Consultation", "Discharge"]

# How long each activity takes (min, max) in minutes. A random value in this
# range is picked every time an activity happens.
ACTIVITY_DURATIONS_MINUTES = {
    "Registration":        (2, 5),
    "Triage":              (5, 15),
    "X-Ray":               (10, 20),
    "Doctor Consultation": (10, 25),
    "Discharge":           (2, 5),
}

# Rework rule: after X-Ray, some patients are sent back to Triage
# (e.g. missing paperwork / re-check) and must do X-Ray again.
LOOP_BACK_RULE = {
    "after_activity": "X-Ray",
    "loop_back_to": "Triage",
    "probability": 0.35,       # 35% -> inside the 30-40% range required by the brief
}

# Idle time between activities (minutes), added ON TOP of activity duration.
# This is what makes the timeline look like a real, busy hospital.
WAIT_TIME_MINUTES = (5, 45)


# ---------------------------------------------------------------------------
# 2. ONE PATIENT'S JOURNEY
# ---------------------------------------------------------------------------

def generate_patient_journey(patient_id, start_time):
    """
    Simulate one patient from arrival to discharge.

    Returns:
        events      - list of dicts {Case_ID, Activity_Name, Timestamp}
        looped_back - True if this patient went through the rework loop
    """
    events = []
    current_time = start_time

    # Start from the happy path, then possibly insert the rework loop.
    activity_sequence = list(HAPPY_PATH)

    looped_back = random.random() < LOOP_BACK_RULE["probability"]
    if looped_back:
        # Result: ... X-Ray, Triage, X-Ray, Doctor Consultation ...
        xray_index = activity_sequence.index(LOOP_BACK_RULE["after_activity"])
        activity_sequence = (
            activity_sequence[: xray_index + 1]
            + [LOOP_BACK_RULE["loop_back_to"], LOOP_BACK_RULE["after_activity"]]
            + activity_sequence[xray_index + 1:]
        )

    # Walk through the sequence, moving the clock forward as we go.
    for i, activity in enumerate(activity_sequence):
        # Waiting happens BEFORE every activity except the first one.
        if i > 0:
            current_time += timedelta(minutes=random.randint(*WAIT_TIME_MINUTES))

        # Record when this activity STARTS.
        events.append({
            "Case_ID": patient_id,
            "Activity_Name": activity,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Then the activity itself takes some time.
        min_dur, max_dur = ACTIVITY_DURATIONS_MINUTES[activity]
        current_time += timedelta(minutes=random.randint(min_dur, max_dur))

    return events, looped_back


# ---------------------------------------------------------------------------
# 3. MANY PATIENTS
# ---------------------------------------------------------------------------

def generate_multiple_patients(num_patients):
    """
    Simulate many patients arriving one after another.

    Arrival times are cumulative: each patient arrives a few minutes after the
    previous one, so arrivals stay steady no matter how many patients we make.
    (Day 4/5 used randint * i, which spaced late patients further and further
    apart - that broke down at thousands of patients.)

    Returns:
        all_events      - one flat list of every event for every patient
        loop_back_count - how many patients went through the rework loop
    """
    all_events = []
    loop_back_count = 0
    arrival_time = START_TIME

    for i in range(1, num_patients + 1):
        patient_id = f"P{i:04d}"          # P0001 ... P2000 (4 digits so IDs sort correctly)
        arrival_time += timedelta(minutes=random.randint(*ARRIVAL_GAP_MINUTES))

        patient_events, looped_back = generate_patient_journey(patient_id, arrival_time)
        all_events.extend(patient_events)
        loop_back_count += looped_back

    return all_events, loop_back_count


# ---------------------------------------------------------------------------
# 4. BUILD, SORT AND EXPORT
# ---------------------------------------------------------------------------

def build_event_log(num_patients=NUM_PATIENTS):
    """Create the final DataFrame: 3 columns, sorted by patient then time."""
    events, loop_back_count = generate_multiple_patients(num_patients)
    df = pd.DataFrame(events, columns=["Case_ID", "Activity_Name", "Timestamp"])

    # Timestamps are zero-padded ISO strings, so sorting them as text is
    # the same as sorting them chronologically.
    df = df.sort_values(["Case_ID", "Timestamp"]).reset_index(drop=True)
    return df, loop_back_count


if __name__ == "__main__":
    random.seed(SEED)

    df, loop_back_count = build_event_log()
    df.to_csv(OUTPUT_FILE, index=False)

    n_patients = df["Case_ID"].nunique()
    print(f"Saved {OUTPUT_FILE}")
    print(f"Patients: {n_patients}")
    print(f"Events:   {len(df)}")
    print(f"Loop-backs (X-Ray -> Triage): {loop_back_count} ({loop_back_count / n_patients:.1%})")