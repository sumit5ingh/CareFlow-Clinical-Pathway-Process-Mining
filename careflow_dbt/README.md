# CareFlow - Week 2: dbt & BigQuery Event Normalization

## Overview

This folder contains the dbt implementation for Week 2 of the CareFlow: Clinical Pathway Process Mining project.

The objective of Week 2 was to transform the raw EHR event log stored in BigQuery into a clean, standardized event log that can be used by PM4Py for process discovery and pathway analysis.

## My Role

**Member 2 - dbt & BigQuery (Event Normalization)**

## Objective

The main objectives of my work were:

- Connect dbt with BigQuery.
- Use the Week 1 raw EHR event log as a dbt source.
- Standardize event column names and data types.
- Remove records with missing required values.
- Create a clean event log for process mining.
- Validate the transformed data.
- Prepare the final dataset for Member 3's PM4Py process discovery work.

## Data Source

The raw event data was created during Week 1 and stored in BigQuery.

**Google Cloud Project:** `aerial-episode-509608-t7`

**Raw Dataset:** `careflow_raw`

**Raw Table:** `ehr_event_log_raw`

The raw event log contains:

- `Case_ID`
- `Activity_Name`
- `Timestamp`

## dbt Target

The transformed models are stored in:

**Dataset:** `careflow_analytics`

The final event log contains:

- `case_id`
- `activity_name`
- `event_timestamp`

## dbt Models

### 1. Staging Model

`stg_ehr_event_log.sql`

The staging model:

- Reads data from the BigQuery raw table.
- Converts `Case_ID` to `case_id`.
- Converts `Activity_Name` to `activity_name`.
- Converts `Timestamp` to `event_timestamp`.
- Trims activity names.
- Filters out records with missing case IDs, activities, or timestamps.

### 2. Final Event Log

`event_log.sql`

The final model provides a standardized chronological event log for process mining.

Events are organized using:

`case_id → event_timestamp`

This structure allows PM4Py to reconstruct individual patient pathways and analyze transitions between hospital activities.

## Data Quality

dbt tests were used to validate important columns and ensure that:

- Case IDs are not NULL.
- Activity names are not NULL.
- Event timestamps are not NULL.

The transformed data was also checked for chronological ordering and activity transitions.

## BigQuery Validation

The final model was validated using BigQuery queries to check:

- Total number of events.
- NULL values.
- Patient event ordering.
- Activity transitions.
- Overall structure of the transformed event log.

## Process-Mining Readiness

The final `event_log` model is prepared for the next stage of the project.

Member 3 can use this dataset with PM4Py to perform:

- Process discovery.
- Patient pathway analysis.
- Directly-Follows Graph analysis.
- Spaghetti diagram generation.
- Bottleneck identification.
- Loop-back analysis.

## Technology Stack

- Google BigQuery
- dbt
- Python
- SQL
- Git/GitHub

## Week 2 Deliverable

The main deliverable is a clean and standardized BigQuery event log generated through dbt and ready for PM4Py-based clinical pathway analysis.

## Next Step

The normalized `event_log` dataset will be used by Member 3 for process discovery and clinical pathway mining.