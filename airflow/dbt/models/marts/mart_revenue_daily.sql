{{ config(materialized='table') }}

SELECT
    toDate(payment_date) AS day,
    sum(amount) AS revenue
FROM {{ ref('int_payments_success') }}
GROUP BY day
ORDER BY day
