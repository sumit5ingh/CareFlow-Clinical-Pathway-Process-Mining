# CareFlow Clinical Pathway Process Mining

## Member 4 – Loading & Validation

### 1. BigQuery Configuration

| Item | Value |
|---|---|
| Project ID | `aerial-episode-509608-t7` |
| Dataset | `careflow_raw` |
| Table | `ehr_event_log_raw` |

### 2. Table Schema

| Column | Data Type |
|---|---|
| Case_ID | STRING |
| Activity_Name | STRING |
| Timestamp | TIMESTAMP |

### 3. Data Loading

The EHR event log was successfully loaded into BigQuery.

Total records loaded:

**11,410**

### 4. Validation Checks

| Validation Check | Expected | Actual | Status |
|---|---:|---:|---|
| Total Records | 11,410 | 11,410 | PASS |
| NULL Case_ID | 0 | 0 | PASS |
| NULL Activity_Name | 0 | 0 | PASS |
| NULL Timestamp | 0 | 0 | PASS |
| Duplicate Events | 0 | 0 | PASS |
| Unique Cases | 2000 | 2000 | PASS |
| Chronological Errors | 0 | 0 | PASS |

### 5. Activity Distribution

The activity distribution was checked using the `Activity_Name`
field to identify the frequency of each clinical activity.
Row	Activity_Name	event_count
1	Triage	            2705
2	X-Ray	            2705
3	Discharge	        2000
4	Doctor Consultation	2000
5	Registration	    2000

### 6. Timestamp Validation

The minimum and maximum timestamps were checked to identify
the time range covered by the event log.

Row	first_event	                     last_event
1	2026-09-15 08:03:00 UTC	     2026-09-23 19:47:00 UTC

### 7. Chronological Order Validation

Events were checked within each `Case_ID` to identify whether
any event occurred before its previous event.

### 8. Events Per Case

The number of events associated with each `Case_ID` was calculated
to verify the structure of individual clinical cases.


### 9. Conclusion

The EHR event log was loaded into BigQuery and validated using
record count, NULL checks, duplicate checks, unique case counts,
activity distribution, timestamp range, chronological ordering,
and events-per-case analysis.