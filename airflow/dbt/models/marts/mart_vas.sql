{{ config(materialized='table') }}

SELECT
    v.vas_type_id,
    v.vas_type_name,
    count(*) AS purchases,
    sum(p.amount) AS revenue
FROM {{ ref('int_payments_success') }} p
JOIN {{ ref('dim_vas_types') }} v ON p.vas_type_id = v.vas_type_id
WHERE p.payment_type = 'vas'
GROUP BY v.vas_type_id, v.vas_type_name
ORDER BY revenue DESC
