

SELECT
    user_id,
    email,
    phone,
    status,
    registered_at,
    created_at,
    updated_at
FROM s3(
    'http://minio:9000/raw/postgres/users/*.parquet',
    'Parquet',
    'user_id Int64, email String, phone Nullable(String), status String, registered_at DateTime64(3), created_at DateTime64(3), updated_at DateTime64(3)'
)