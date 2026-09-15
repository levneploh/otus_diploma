{{ config(materialized='view') }}

SELECT
    l.listing_id,
    l.user_id,
    l.category_id,
    c.name AS category_name,
    l.title,
    l.price,
    l.status,
    l.platform,
    l.created_at,
    l.sold_at
FROM {{ ref('stg_listings') }} l
LEFT JOIN {{ ref('stg_categories') }} c ON l.category_id = c.category_id
