-- ============================================================
-- CareFlow: Clinical Pathway Process Mining
-- Week 1 - BigQuery Warehouse Setup
-- Member 2
-- ============================================================

-- Dataset: careflow_raw
-- Table: ehr_event_log_raw
-- Schema:
-- Case_ID        STRING
-- Activity_Name  STRING
-- Timestamp      TIMESTAMP


-- 1. Check sample records

SELECT *
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`
LIMIT 20;


-- 2. Check total number of event records

SELECT
    COUNT(*) AS total_records
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`;


-- 3. Check number of unique patient cases

SELECT
    COUNT(DISTINCT Case_ID) AS total_cases
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`;


-- 4. Check activity distribution

SELECT
    Activity_Name,
    COUNT(*) AS event_count
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`
GROUP BY Activity_Name
ORDER BY event_count DESC;


-- 5. Check timestamp range

SELECT
    MIN(Timestamp) AS first_event,
    MAX(Timestamp) AS last_event
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`;


-- 6. Check for NULL values

SELECT
    COUNTIF(Case_ID IS NULL) AS null_case_id,
    COUNTIF(Activity_Name IS NULL) AS null_activity_name,
    COUNTIF(Timestamp IS NULL) AS null_timestamp
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`;


-- 7. Check chronological patient events

SELECT
    Case_ID,
    Activity_Name,
    Timestamp
FROM `YOUR_PROJECT_ID.careflow_raw.ehr_event_log_raw`
ORDER BY Case_ID, Timestamp
LIMIT 50;