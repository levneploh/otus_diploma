

SELECT
    listing_id,
    user_id,
    category_id,
    title,
    description,
    price,
    status,
    platform,
    created_at,
    activated_at,
    sold_at,
    deactivated_at,
    updated_at
FROM s3(
    'http://minio:9000/raw/postgres/listings/*.parquet',
    'Parquet',
    'listing_id Int64, user_id Int64, category_id Int32, title String, description Nullable(String), price Float64, status String, platform String, created_at DateTime64(3), activated_at Nullable(DateTime64(3)), sold_at Nullable(DateTime64(3)), deactivated_at Nullable(DateTime64(3)), updated_at DateTime64(3)'
)