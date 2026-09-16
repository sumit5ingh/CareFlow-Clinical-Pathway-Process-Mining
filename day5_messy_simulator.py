import pandas as pd
import random
from datetime import datetime, timedelta

# ---- Carried over from Day 1/2/4 ----
HAPPY_PATH = ["Registration", "Triage", "X-Ray", "Doctor Consultation", "Discharge"]

ACTIVITY_DURATIONS_MINUTES = {
    "Registration":        (2, 5),
    "Triage":              (5, 15),
    "X-Ray":               (10, 20),
    "Doctor Consultation": (10, 25),
    "Discharge":           (2, 5),
}

# ---- New for Day 5 ----

# After X-Ray, this % chance the patient gets bounced back to Triage
# (simulating missing paperwork / re-check before consultation)
LOOP_BACK_RULE = {
    "after_activity": "X-Ray",
    "loop_back_to": "Triage",
    "probability": 0.35,   # 35% -> falls inside the 30-40% range from the brief
}

# Random idle/wait time injected BETWEEN activities (on top of activity duration)
# so the timeline doesn't look artificially clean/instant.
WAIT_TIME_MINUTES = (5, 45)


def generate_patient_journey(patient_id, start_time):
    """
    Simulates ONE patient's journey, now with:
      - the happy path activity durations (Day 1/2/4)
      - a probabilistic loop-back from X-Ray -> Triage (Day 5)
      - random wait time between consecutive activities (Day 5)

    Returns a list of event dicts, same shape as before:
    {Case_ID, Activity_Name, Timestamp}
    """
    events = []
    current_time = start_time

    # Build the activity sequence for this patient (may include a loop-back)
    activity_sequence = list(HAPPY_PATH)

    looped_back = False
    if random.random() < LOOP_BACK_RULE["probability"]:
        looped_back = True
        xray_index = activity_sequence.index(LOOP_BACK_RULE["after_activity"])
        # Insert an extra Triage -> X-Ray round-trip right after the original X-Ray
        activity_sequence = (
            activity_sequence[: xray_index + 1]
            + [LOOP_BACK_RULE["loop_back_to"], LOOP_BACK_RULE["after_activity"]]
            + activity_sequence[xray_index + 1:]
        )

    for i, activity in enumerate(activity_sequence):
        # Add random wait time before every activity except the very first one
        if i > 0:
            wait = random.randint(*WAIT_TIME_MINUTES)
            current_time += timedelta(minutes=wait)

        min_dur, max_dur = ACTIVITY_DURATIONS_MINUTES[activity]
        duration = random.randint(min_dur, max_dur)

        events.append({
            "Case_ID": patient_id,
            "Activity_Name": activity,
            "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        current_time += timedelta(minutes=duration)

    return events, looped_back


def generate_multiple_patients(num_patients=25):
    """
    Loops generate_patient_journey() for many patients and combines all
    their events into a single flat list - same shape needed for the
    event log DataFrame as Day 4, plus a quick loop-back count for sanity-checking.
    """
    all_events = []
    base_time = datetime(2026, 9, 15, 8, 0, 0)
    loop_back_count = 0

    for i in range(1, num_patients + 1):
        patient_id = f"P{i:03d}"
        arrival_offset = timedelta(minutes=random.randint(2, 10) * i)
        patient_start = base_time + arrival_offset

        patient_events, looped_back = generate_patient_journey(patient_id, patient_start)
        all_events.extend(patient_events)
        if looped_back:
            loop_back_count += 1

    return all_events, loop_back_count


if __name__ == "__main__":
    simulated_log, loop_back_count = generate_multiple_patients(25)
    df_simulated = pd.DataFrame(simulated_log)

    print(f"Total events generated: {len(df_simulated)}")
    print(f"Total patients: {df_simulated['Case_ID'].nunique()}")
    print(f"Patients with X-Ray -> Triage loop-back: {loop_back_count} "
          f"({loop_back_count / df_simulated['Case_ID'].nunique():.0%})")
    print()
    print(df_simulated.to_string(index=False))


