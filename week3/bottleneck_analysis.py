import os
import pandas as pd

# =========================================================
# CAREFLOW CLINICAL PATHWAY PROCESS MINING
# WEEK 3 - MEMBER 2
# BOTTLENECK / WAITING-TIME ANALYSIS
# =========================================================

INPUT_FILE = "data/event_log.csv"
OUTPUT_FOLDER = "week3/outputs"

# Create output folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# =========================================================
# 1. LOAD DATA
# =========================================================

df = pd.read_csv(INPUT_FILE)

print("========================================")
print("CAREFLOW WEEK 3")
print("BOTTLENECK / WAITING-TIME ANALYSIS")
print("========================================")

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

print("\nColumns:")
print(df.columns.tolist())


# =========================================================
# 2. CHECK REQUIRED COLUMNS
# =========================================================

required_columns = [
    "case_id",
    "activity_name",
    "event_timestamp"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column '{column}' is missing."
        )


# =========================================================
# 3. CLEAN DATA
# =========================================================

df["event_timestamp"] = pd.to_datetime(
    df["event_timestamp"],
    errors="coerce"
)

# Remove rows with missing required information
df = df.dropna(
    subset=required_columns
)

# Sort events by case and timestamp
df = df.sort_values(
    ["case_id", "event_timestamp"]
).reset_index(drop=True)


print("\nValid records:", len(df))
print("Number of cases:", df["case_id"].nunique())


# =========================================================
# 4. FIND PREVIOUS ACTIVITY
# =========================================================

df["previous_activity"] = (
    df.groupby("case_id")["activity_name"].shift(1)
)

df["previous_timestamp"] = (
    df.groupby("case_id")["event_timestamp"].shift(1)
)


# =========================================================
# 5. CALCULATE WAITING TIME
# =========================================================

df["waiting_time_minutes"] = (
    df["event_timestamp"]
    - df["previous_timestamp"]
).dt.total_seconds() / 60


# =========================================================
# 6. REMOVE FIRST EVENT OF EACH CASE
# =========================================================

transitions = df.dropna(
    subset=[
        "previous_activity",
        "previous_timestamp",
        "waiting_time_minutes"
    ]
).copy()


# Rename current activity
transitions = transitions.rename(
    columns={
        "activity_name": "current_activity"
    }
)


# =========================================================
# 7. CREATE TRANSITION
# =========================================================

transitions["transition"] = (
    transitions["previous_activity"]
    + " -> "
    + transitions["current_activity"]
)


# =========================================================
# 8. SAVE DETAILED WAITING-TIME DATA
# =========================================================

detail_columns = [
    "case_id",
    "previous_activity",
    "current_activity",
    "previous_timestamp",
    "event_timestamp",
    "waiting_time_minutes",
    "transition"
]

transitions[detail_columns].to_csv(
    f"{OUTPUT_FOLDER}/waiting_time_details.csv",
    index=False
)


# =========================================================
# 9. TRANSITION WAITING-TIME ANALYSIS
# =========================================================

transition_summary = (
    transitions
    .groupby("transition")
    .agg(
        number_of_cases=("case_id", "count"),
        average_wait_minutes=(
            "waiting_time_minutes",
            "mean"
        ),
        median_wait_minutes=(
            "waiting_time_minutes",
            "median"
        ),
        maximum_wait_minutes=(
            "waiting_time_minutes",
            "max"
        ),
        minimum_wait_minutes=(
            "waiting_time_minutes",
            "min"
        )
    )
    .reset_index()
)


# Sort from highest average waiting time
transition_summary = transition_summary.sort_values(
    "average_wait_minutes",
    ascending=False
)


# Save transition summary
transition_summary.to_csv(
    f"{OUTPUT_FOLDER}/transition_waiting_summary.csv",
    index=False
)


# =========================================================
# 10. ACTIVITY WAITING-TIME ANALYSIS
# =========================================================

activity_summary = (
    transitions
    .groupby("current_activity")
    .agg(
        number_of_transitions=("case_id", "count"),
        average_incoming_wait_minutes=(
            "waiting_time_minutes",
            "mean"
        ),
        median_incoming_wait_minutes=(
            "waiting_time_minutes",
            "median"
        ),
        maximum_incoming_wait_minutes=(
            "waiting_time_minutes",
            "max"
        )
    )
    .reset_index()
)


activity_summary = activity_summary.sort_values(
    "average_incoming_wait_minutes",
    ascending=False
)


activity_summary.to_csv(
    f"{OUTPUT_FOLDER}/activity_waiting_summary.csv",
    index=False
)


# =========================================================
# 11. IDENTIFY TOP BOTTLENECKS
# =========================================================

top_bottlenecks = transition_summary.head(5)


top_bottlenecks.to_csv(
    f"{OUTPUT_FOLDER}/top_bottlenecks.csv",
    index=False
)


# =========================================================
# 12. CREATE TEXT SUMMARY
# =========================================================

summary_file = (
    f"{OUTPUT_FOLDER}/bottleneck_summary.txt"
)

with open(
    summary_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "CAREFLOW WEEK 3 - BOTTLENECK ANALYSIS\n"
    )

    file.write("=" * 50 + "\n\n")

    file.write(
        f"Valid events analyzed: {len(df)}\n"
    )

    file.write(
        f"Cases analyzed: "
        f"{df['case_id'].nunique()}\n"
    )

    file.write(
        f"Transitions analyzed: "
        f"{len(transitions)}\n\n"
    )

    file.write(
        "TOP 5 TRANSITIONS BY "
        "AVERAGE WAITING TIME\n"
    )

    file.write("-" * 50 + "\n")

    for _, row in top_bottlenecks.iterrows():

        file.write(
            f"{row['transition']} | "
            f"Average: "
            f"{row['average_wait_minutes']:.2f} minutes | "
            f"Median: "
            f"{row['median_wait_minutes']:.2f} minutes | "
            f"Observations: "
            f"{int(row['number_of_cases'])}\n"
        )


# =========================================================
# 13. DISPLAY RESULTS
# =========================================================

print("\n========================================")
print("TOP 5 POTENTIAL BOTTLENECKS")
print("========================================")

print(
    top_bottlenecks.to_string(index=False)
)

print("\n========================================")
print("OUTPUT FILES CREATED")
print("========================================")

print("1. waiting_time_details.csv")
print("2. transition_waiting_summary.csv")
print("3. activity_waiting_summary.csv")
print("4. top_bottlenecks.csv")
print("5. bottleneck_summary.txt")

print("\nAnalysis completed successfully!")