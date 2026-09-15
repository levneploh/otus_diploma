{{ config(materialized='table') }}

SELECT
    category_id,
    name AS category_name,
    parent_id
FROM {{ ref('stg_categories') }}
