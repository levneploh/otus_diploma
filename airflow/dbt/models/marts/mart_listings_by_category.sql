{{ config(materialized='table') }}

SELECT
    category_id,
    category_name,
    count(*) AS listing_count,
    round(avg(price), 2) AS avg_price
FROM {{ ref('int_listings_enriched') }}
GROUP BY category_id, category_name
ORDER BY listing_count DESC
