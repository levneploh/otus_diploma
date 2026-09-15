{{ config(materialized='table') }}

SELECT
    toDate(ts) AS day,
    platform,
    uniqExact(user_id) AS dau
FROM {{ ref('stg_user_activity') }}
GROUP BY day, platform
ORDER BY day, platform
