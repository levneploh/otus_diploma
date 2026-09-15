{{ config(materialized='view') }}

SELECT
    event_id,
    user_id,
    event_type,
    platform,
    listing_id,
    session_id,
    ts
FROM s3(
    '{{ var('minio_endpoint') }}/raw/kafka/user_activity/*.parquet',
    'Parquet',
    'event_id String, user_id Int64, event_type String, platform String, listing_id Nullable(Int64), session_id String, ts DateTime64(3)'
)
