import os
import pandas as pd
import pm4py
from collections import Counter


# =========================================================
# 1. FILE PATHS
# =========================================================

INPUT_FILE = "data/event_log.csv"
OUTPUT_FOLDER = "week2/outputs"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# =========================================================
# 2. LOAD EVENT LOG
# =========================================================

print("\nLoading event log...")

df = pd.read_csv("data/event_log.csv")

print("\nFirst 10 rows:")
print(df.head(10))

print("\nColumns:")
print(df.columns)

print("\nDataset shape:")
print(df.shape)


# =========================================================
# 3. CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "case_id",
    "activity_name",
    "event_timestamp"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(f"Missing required column: {column}")

print("\nRequired columns are present.")


# =========================================================
# 4. CHECK NULL VALUES
# =========================================================

print("\nNull value check:")
print(df[required_columns].isnull().sum())


# =========================================================
# 5. CONVERT TIMESTAMP
# =========================================================

df["event_timestamp"] = pd.to_datetime(
    df["event_timestamp"]
)

print("\nTimestamp conversion completed.")


# =========================================================
# 6. SORT EVENT LOG
# =========================================================

df = df.sort_values(
    by=["case_id", "event_timestamp"]
).reset_index(drop=True)

print("\nEvent log sorted by case and timestamp.")


# =========================================================
# 7. BASIC PROCESS STATISTICS
# =========================================================

number_of_cases = df["case_id"].nunique()
number_of_events = len(df)
number_of_activities = df["activity_name"].nunique()

print("\n========== PROCESS STATISTICS ==========")
print("Number of cases:", number_of_cases)
print("Number of events:", number_of_events)
print("Unique activities:", number_of_activities)


# =========================================================
# 8. ACTIVITY FREQUENCY
# =========================================================

activity_frequency = (
    df["activity_name"]
    .value_counts()
    .reset_index()
)

activity_frequency.columns = [
    "activity_name",
    "event_count"
]

activity_frequency.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "activity_frequency.csv"
    ),
    index=False
)

print("\nActivity frequency:")
print(activity_frequency)


# =========================================================
# 9. EVENTS PER CASE
# =========================================================

events_per_case = (
    df.groupby("case_id")
    .size()
    .reset_index(name="event_count")
)

events_per_case.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "events_per_case.csv"
    ),
    index=False
)


# =========================================================
# 10. CASE DURATION
# =========================================================

case_duration = (
    df.groupby("case_id")["event_timestamp"]
    .agg(["min", "max"])
    .reset_index()
)

case_duration["duration_minutes"] = (
    case_duration["max"] -
    case_duration["min"]
).dt.total_seconds() / 60

case_duration.columns = [
    "case_id",
    "start_time",
    "end_time",
    "duration_minutes"
]

case_duration.to_csv(
    os.path.join(
        OUTPUT_FOLDER,
        "case_duration.csv"
    ),
    index=False
)

print("\nCase duration calculated.")


# =========================================================
# 11. CREATE PM4PY EVENT LOG
# =========================================================

print("\nCreating PM4Py event log...")

event_log = pm4py.format_dataframe(
    df,
    case_id="case_id",
    activity_key="activity_name",
    timestamp_key="event_timestamp"
)

print("PM4Py event log created.")


# =========================================================
# 12. DIRECTLY-FOLLOWS GRAPH (DFG)
# =========================================================

print("\nDiscovering Directly-Follows Graph...")

dfg, start_activities, end_activities = (
    pm4py.discover_dfg(event_log)
)

dfg_path = os.path.join(
    OUTPUT_FOLDER,
    "dfg.png"
)

pm4py.save_vis_dfg(
    dfg,
    start_activities,
    end_activities,
    dfg_path
)

print("DFG saved:", dfg_path)


# =========================================================
# 13. PETRI NET - ALPHA MINER
# =========================================================

print("\nDiscovering Petri Net using Alpha Miner...")

net, initial_marking, final_marking = (
    pm4py.discover_petri_net_alpha(event_log)
)

petri_path = os.path.join(
    OUTPUT_FOLDER,
    "petri_net.png"
)

pm4py.save_vis_petri_net(
    net,
    initial_marking,
    final_marking,
    petri_path
)

print("Petri Net saved:", petri_path)


# =========================================================
# 14. HEURISTICS MINER
# =========================================================

print("\nDiscovering Heuristics Miner...")

heu_net = pm4py.discover_heuristics_net(
    event_log
)

heuristics_path = os.path.join(
    OUTPUT_FOLDER,
    "heuristics_net.png"
)

pm4py.save_vis_heuristics_net(
    heu_net,
    heuristics_path
)

print("Heuristics Net saved:", heuristics_path)


# =========================================================
# 15. TOP PATIENT PATHWAYS
# =========================================================

print("\nCalculating patient pathways...")

pathways = (
    df.groupby("case_id")["activity_name"]
    .apply(list)
)

pathway_strings = [
    " -> ".join(path)
    for path in pathways
]

pathway_counts = Counter(pathway_strings)

top_pathways = pathway_counts.most_common(10)

top_pathways_file = os.path.join(
    OUTPUT_FOLDER,
    "top_pathways.txt"
)

with open(
    top_pathways_file,
    "w",
    encoding="utf-8"
) as file:

    file.write("TOP 10 PATIENT PATHWAYS\n")
    file.write("=" * 60 + "\n\n")

    for rank, (pathway, count) in enumerate(
        top_pathways,
        start=1
    ):

        file.write(
            f"{rank}. {count} cases : {pathway}\n"
        )

print("Top pathways saved:", top_pathways_file)


# =========================================================
# 16. START AND END ACTIVITIES
# =========================================================

print("\nStart activities:")
print(start_activities)

print("\nEnd activities:")
print(end_activities)


# =========================================================
# 17. LOOP-BACK ANALYSIS
# =========================================================

print("\nAnalyzing loop-back activities...")

loopbacks = []

for case_id, group in df.groupby("case_id"):

    activities = group["activity_name"].tolist()

    for i in range(1, len(activities)):

        if activities[i] in activities[:i]:

            loopbacks.append(
                (
                    case_id,
                    activities[i - 1],
                    activities[i]
                )
            )

loopback_file = os.path.join(
    OUTPUT_FOLDER,
    "loopback_analysis.txt"
)

with open(
    loopback_file,
    "w",
    encoding="utf-8"
) as file:

    file.write("LOOP-BACK ANALYSIS\n")
    file.write("=" * 60 + "\n\n")

    file.write(
        f"Total loop-back events: {len(loopbacks)}\n\n"
    )

    for item in loopbacks[:100]:

        file.write(
            f"Case {item[0]} : "
            f"{item[1]} -> {item[2]}\n"
        )

print("Loop-back analysis saved:", loopback_file)


# =========================================================
# 18. PROCESS SUMMARY
# =========================================================

summary_file = os.path.join(
    OUTPUT_FOLDER,
    "process_summary.txt"
)

with open(
    summary_file,
    "w",
    encoding="utf-8"
) as file:

    file.write("CAREFLOW PROCESS MINING SUMMARY\n")
    file.write("=" * 60 + "\n\n")

    file.write(
        f"Number of cases: {number_of_cases}\n"
    )

    file.write(
        f"Number of events: {number_of_events}\n"
    )

    file.write(
        f"Unique activities: {number_of_activities}\n\n"
    )

    file.write("Activities:\n")

    for activity in sorted(
        df["activity_name"].unique()
    ):

        file.write(
            f"- {activity}\n"
        )

    file.write("\nStart activities:\n")

    for activity, count in start_activities.items():

        file.write(
            f"- {activity}: {count}\n"
        )

    file.write("\nEnd activities:\n")

    for activity, count in end_activities.items():

        file.write(
            f"- {activity}: {count}\n"
        )

print("Process summary saved:", summary_file)


# =========================================================
# 19. FINISHED
# =========================================================

print("\n==========================================")
print("PM4Py PROCESS MINING COMPLETED")
print("==========================================")

print("\nGenerated files:")

for filename in os.listdir(OUTPUT_FOLDER):

    print("-", filename)