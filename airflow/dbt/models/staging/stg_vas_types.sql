{{ config(materialized='view') }}

SELECT
    vas_type_id,
    name,
    description
FROM s3(
    '{{ var('minio_endpoint') }}/raw/mysql/vas_types/*.parquet',
    'Parquet',
    'vas_type_id Int32, name String, description Nullable(String)'
)
