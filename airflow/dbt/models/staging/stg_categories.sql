{{ config(materialized='view') }}

SELECT
    category_id,
    name,
    parent_id
FROM s3(
    '{{ var('minio_endpoint') }}/raw/mysql/categories/*.parquet',
    'Parquet',
    'category_id Int32, name String, parent_id Nullable(Int32)'
)
