{{ config(materialized='view') }}

SELECT
    payment_id,
    user_id,
    listing_id,
    vas_type_id,
    amount,
    payment_type,
    status,
    payment_date
FROM s3(
    '{{ var('minio_endpoint') }}/raw/postgres/payments/*.parquet',
    'Parquet',
    'payment_id Int64, user_id Int64, listing_id Nullable(Int64), vas_type_id Nullable(Int32), amount Float64, payment_type String, status String, payment_date DateTime64(3)'
)
