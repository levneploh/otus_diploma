{{ config(materialized='table') }}

WITH monthly AS (
    SELECT
        toStartOfMonth(payment_date) AS month,
        sum(amount) AS revenue
    FROM {{ ref('int_payments_success') }}
    GROUP BY month
)
SELECT
    m.month,
    m.revenue,
    p.revenue AS revenue_prev_year,
    round((m.revenue - p.revenue) / p.revenue, 4) AS yoy_growth
FROM monthly m
LEFT JOIN monthly p ON p.month = addMonths(m.month, -12)
ORDER BY m.month
