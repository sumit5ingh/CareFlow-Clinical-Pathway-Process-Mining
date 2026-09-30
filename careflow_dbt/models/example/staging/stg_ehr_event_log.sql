SELECT
    CAST(Case_ID AS STRING) AS case_id,
    TRIM(Activity_Name) AS activity_name,
    CAST(Timestamp AS TIMESTAMP) AS event_timestamp
FROM {{ source('careflow_raw', 'ehr_event_log_raw') }}
WHERE Case_ID IS NOT NULL
  AND Activity_Name IS NOT NULL
  AND Timestamp IS NOT NULL