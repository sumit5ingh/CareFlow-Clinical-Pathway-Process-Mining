# CareFlow Clinical Pathway Process Mining

## Week 2 – Member 3
### PM4Py Process Discovery / Pathway Mining

## 1. Objective

To discover and analyze clinical process pathways from
the validated EHR event log using PM4Py.

## 2. Input Data

- Case ID: Case_ID
- Activity: Activity_Name
- Timestamp: Timestamp

## 3. Tools Used

- Python
- Pandas
- PM4Py

## 4. Process Discovery

The event log was converted into a PM4Py event log
and process discovery algorithms were applied.

Algorithms used:
- Alpha Miner
- Heuristics Miner
- Directly-Follows Graph (DFG)

## 5. Process Statistics

- Total cases: [2000]
- Total events: [11410]
- Unique activities: [5]

## 6. Most Frequent Activities

Activity_Name
Triage                 2705
X-Ray                  2705
Registration           2000
Doctor Consultation    2000
Discharge              2000

## 7. Most Frequent Clinical Pathways

1295 : Registration → Triage → X-Ray → Doctor Consultation → Discharge
705 : Registration → Triage → X-Ray → Triage → X-Ray → Doctor Consultation → Discharge

## 8. Process Model

The discovered process model was generated using PM4Py.

## 9. Conclusion

The process discovery analysis identifies the common clinical
pathways and variations present in the EHR event log.
The discovered process models can be used for further
clinical pathway analysis and dashboard reporting.