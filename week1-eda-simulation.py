import pandas as pd
from datetime import datetime
import random

sample_event_log = [
    {"Case_ID": "P001", "Activity_Name": "Registration",       "Timestamp": "2026-09-13 09:00:00"},
    {"Case_ID": "P001", "Activity_Name": "Triage",              "Timestamp": "2026-09-13 09:15:00"},
    {"Case_ID": "P001", "Activity_Name": "X-Ray",               "Timestamp": "2026-09-13 09:40:00"},
    {"Case_ID": "P001", "Activity_Name": "Doctor Consultation", "Timestamp": "2026-09-13 10:10:00"},
    {"Case_ID": "P001", "Activity_Name": "Discharge",           "Timestamp": "2026-09-13 10:30:00"},
]

df_sample = pd.DataFrame (sample_event_log)
print(df_sample)

HAPPY_PATH = ["Registration", "Triage", "X-Ray", "Doctor Consultation", "Discharge"]

LOOP_BACK_RULE = {
    "after_activity": "X-Ray",
    "loop_back_to": "Triage",
    "probability": 0.35
}

ACTIVITY_DURATIONS_MINUTES = {
    "Registration":        (2, 5),
    "Triage":              (5, 15),
    "X-Ray":               (10, 20),
    "Doctor Consultation": (10, 25),
    "Discharge":           (2, 5),
}

print(HAPPY_PATH)
print(LOOP_BACK_RULE)
print(ACTIVITY_DURATIONS_MINUTES)