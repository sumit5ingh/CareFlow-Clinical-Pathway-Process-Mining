-- =========================================================
-- CAREFLOW CLINICAL PATHWAY PROCESS MINING
-- MEMBER 4 - LOADING & VALIDATION
-- =========================================================

-- Project: aerial-episode-509608-t7
-- Dataset: careflow_raw
-- Table: ehr_event_log_raw


-- =========================================================
-- 1. ROW COUNT VALIDATION
-- =========================================================

SELECT
  COUNT(*) AS total_records
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`;


-- =========================================================
-- 2. NULL VALUE VALIDATION
-- =========================================================

SELECT
  COUNTIF(Case_ID IS NULL) AS null_case_id,
  COUNTIF(Activity_Name IS NULL) AS null_activity_name,
  COUNTIF(Timestamp IS NULL) AS null_timestamp
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`;


-- =========================================================
-- 3. DUPLICATE EVENT VALIDATION
-- =========================================================

SELECT
  Case_ID,
  Activity_Name,
  Timestamp,
  COUNT(*) AS duplicate_count
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`
GROUP BY
  Case_ID,
  Activity_Name,
  Timestamp
HAVING COUNT(*) > 1;


-- =========================================================
-- 4. UNIQUE CASE VALIDATION
-- =========================================================

SELECT
  COUNT(DISTINCT Case_ID) AS total_cases
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`;


-- =========================================================
-- 5. ACTIVITY DISTRIBUTION VALIDATION
-- =========================================================

SELECT
  Activity_Name,
  COUNT(*) AS event_count
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`
GROUP BY Activity_Name
ORDER BY event_count DESC;


-- =========================================================
-- 6. TIMESTAMP RANGE VALIDATION
-- =========================================================

SELECT
  MIN(Timestamp) AS first_event,
  MAX(Timestamp) AS last_event
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`;


-- =========================================================
-- 7. CHRONOLOGICAL ORDER VALIDATION
-- =========================================================

WITH ordered_events AS (
  SELECT
    Case_ID,
    Activity_Name,
    Timestamp,
    LAG(Timestamp) OVER (
      PARTITION BY Case_ID
      ORDER BY Timestamp
    ) AS previous_timestamp
  FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`
)

SELECT
  Case_ID,
  Activity_Name,
  Timestamp,
  previous_timestamp
FROM ordered_events
WHERE previous_timestamp IS NOT NULL
  AND Timestamp < previous_timestamp;


-- =========================================================
-- 8. EVENTS PER CASE VALIDATION
-- =========================================================

SELECT
  Case_ID,
  COUNT(*) AS event_count
FROM `aerial-episode-509608-t7.careflow_raw.ehr_event_log_raw`
GROUP BY Case_ID
ORDER BY event_count;