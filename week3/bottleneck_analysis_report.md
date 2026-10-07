# CareFlow Clinical Pathway Process Mining

## Week 3 - Bottleneck and Waiting-Time Analysis

### 1. Objective

The objective of this analysis is to identify potential
bottlenecks in the clinical pathway by analyzing the time
interval between consecutive clinical activities.

### 2. Dataset

The analysis was performed using the normalized clinical
event log generated during Week 2.

**Input file:**

`data/event_log.csv`

**Columns:**

- `case_id`
- `activity_name`
- `event_timestamp`

### 3. Methodology

The following steps were performed:

1. Loaded the normalized clinical event log.
2. Converted event timestamps into datetime format.
3. Sorted events by case ID and event timestamp.
4. Identified the previous activity for each event.
5. Calculated the time difference between consecutive events.
6. Converted the waiting intervals into minutes.
7. Grouped the waiting times by activity transition.
8. Calculated average, median, minimum and maximum waiting
   times.
9. Ranked transitions according to average waiting time.
10. Identified the top five transitions as potential
    bottlenecks for further investigation.

### 4. Output Files

The following files were generated:

- `outputs/waiting_time_details.csv`
- `outputs/transition_waiting_summary.csv`
- `outputs/activity_waiting_summary.csv`
- `outputs/top_bottlenecks.csv`
- `outputs/bottleneck_summary.txt`

### 5. Bottleneck Analysis

The waiting-time analysis identified the following top
five activity transitions based on average waiting time:

| Rank | Transition | Cases | Average Waiting Time (minutes) |
|------|------------|------|--------------------------------|
| 1 | Doctor Consultation → Discharge | 2000 | 41.912 |
| 2 | X-Ray → Triage | 705 | 40.492 |
| 3 | X-Ray → Doctor Consultation | 2000 | 39.898 |
| 4 | Triage → X-Ray | 2705 | 34.863 |
| 5 | Registration → Triage | 2000 | 28.514 |

The highest average waiting time was observed between
Doctor Consultation and Discharge, with an average interval
of approximately 41.91 minutes.

X-Ray → Triage had the second-highest average waiting time
of approximately 40.49 minutes, while X-Ray → Doctor
Consultation had an average interval of approximately
39.90 minutes.

These transitions are considered potential bottlenecks
based on the observed time between consecutive recorded
events. The waiting-time interval does not necessarily
represent pure patient waiting time, since it may also
include service time, scheduling, documentation, or other
clinical process delays.

### 6. Interpretation

### 6. Key Findings

- Doctor Consultation → Discharge has the highest average
  waiting interval at 41.912 minutes.
- X-Ray → Triage has an average waiting interval of
  40.492 minutes across 705 observations.
- X-Ray → Doctor Consultation has an average waiting
  interval of 39.898 minutes across 2000 observations.
- Triage → X-Ray has an average waiting interval of
  34.863 minutes and is the most frequently observed
  transition among the identified high-wait transitions,
  with 2705 observations.
- Registration → Triage has the lowest average waiting
  interval among the five identified transitions,
  at 28.514 minutes.

### 7. Conclusion

The waiting-time analysis provides a quantitative view of
delays between consecutive clinical activities.

The identified high-wait transitions can be used by the
team to investigate possible process bottlenecks and
opportunities for improving the clinical pathway.