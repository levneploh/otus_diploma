{{ config(materialized='view') }}

SELECT *
FROM {{ ref('stg_payments') }}
WHERE status = 'success'
