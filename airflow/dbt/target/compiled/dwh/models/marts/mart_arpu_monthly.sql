

WITH revenue AS (
    SELECT
        toStartOfMonth(payment_date) AS month,
        sum(amount) AS revenue
    FROM `dwh`.`int_payments_success`
    GROUP BY month
),
mau AS (
    SELECT
        toStartOfMonth(ts) AS month,
        uniqExact(user_id) AS active_users
    FROM `dwh`.`stg_user_activity`
    GROUP BY month
)
SELECT
    r.month,
    r.revenue,
    m.active_users,
    round(r.revenue / m.active_users, 2) AS arpu
FROM revenue r
JOIN mau m ON m.month = r.month
ORDER BY r.month