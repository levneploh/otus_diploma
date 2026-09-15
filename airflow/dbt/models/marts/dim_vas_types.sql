{{ config(materialized='table') }}

SELECT
    vas_type_id,
    name AS vas_type_name,
    description
FROM {{ ref('stg_vas_types') }}
