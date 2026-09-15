import pandas as pd
import random
from datetime import datetime, timedelta

# ---- Carried over from Day 1/2 ----
HAPPY_PATH = ["Registration", "Triage", "X-Ray", "Doctor Consultation", "Discharge"]

ACTIVITY_DURATIONS_MINUTES = {
    "Registration":        (2, 5),
    "Triage":              (5, 15),
    "X-Ray":               (10, 20),
    "Doctor Consultation": (10, 25),
    "Discharge":           (2, 5),
}


def generate_patient_journey(patient_id, start_time):
    """
    Simulates ONE patient's journey through the happy path:
    Registration -> Triage -> X-Ray -> Doctor Consultation -> Discharge

    Returns a list of event dictionaries (one dict per activity),
    each with the same shape as sample_event_log from Day 1.
    """
    events = []
    current_time = start_time

    for activity in HAPPY_PATH:
        min_dur, max_dur = ACTIVITY_DURATIONS_MINUTES[activity]
        duration = random.randint(min_dur, max_dur)

        events.append({
            "Case_ID": patient_id,
            "Activity_Name": activity,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S")
        })

        current_time += timedelta(minutes=duration)

    return events


def generate_multiple_patients(num_patients=25):
    """
    Loops generate_patient_journey() for many patients and
    combines all their events into a single flat list -
    exactly the shape needed for an event log DataFrame.
    """
    all_events = []
    base_time = datetime(2026, 9, 15, 8, 0, 0)

    for i in range(1, num_patients + 1):
        patient_id = f"P{i:03d}"
        # stagger arrivals so patients don't all start at once
        arrival_offset = timedelta(minutes=random.randint(2, 10) * i)
        patient_start = base_time + arrival_offset

        patient_events = generate_patient_journey(patient_id, patient_start)
        all_events.extend(patient_events)

    return all_events


if __name__ == "__main__":
    simulated_log = generate_multiple_patients(25)
    df_simulated = pd.DataFrame(simulated_log)

    print(f"Total events generated: {len(df_simulated)}")
    print(f"Total patients: {df_simulated['Case_ID'].nunique()}")
    print()
    print(df_simulated.to_string(index=False))