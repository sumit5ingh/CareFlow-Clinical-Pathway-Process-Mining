SELECT
    case_id,
    activity_name,
    event_timestamp
FROM {{ ref('stg_ehr_event_log') }}
ORDER BY case_id, event_timestamp