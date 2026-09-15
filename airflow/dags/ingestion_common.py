"""Shared helpers for ingestion DAGs: sources -> MinIO (Parquet).

Reads from PostgreSQL/MySQL via Airflow connections, writes Parquet to MinIO
(via the S3 connection). The Parquet schema matches the dbt staging models.
"""
import io
import os

import pandas as pd
from airflow.providers.amazon.aws.hooks.s3 import S3Hook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.postgres.hooks.postgres import PostgresHook

RAW_BUCKET = "raw"

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "broker:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "user_activity")


def read_postgres(table: str) -> pd.DataFrame:
    hook = PostgresHook(postgres_conn_id="postgres_source")
    return pd.read_sql(f"SELECT * FROM {table}", con=hook.get_sqlalchemy_engine())


def read_mysql(table: str) -> pd.DataFrame:
    hook = MySqlHook(mysql_conn_id="mysql_source")
    return pd.read_sql(f"SELECT * FROM {table}", con=hook.get_sqlalchemy_engine())


def cast_float(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Cast NUMERIC columns to float64 to match the dbt `Float64` contract."""
    for col in columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")
    return df


def write_parquet(df: pd.DataFrame, key: str) -> None:
    """Write a DataFrame as a single Parquet object into MinIO `raw` bucket."""
    buf = io.BytesIO()
    df.to_parquet(buf, engine="pyarrow", index=False)
    buf.seek(0)
    hook = S3Hook(aws_conn_id="minio")
    hook.load_bytes(buf.read(), key=key, bucket_name=RAW_BUCKET, replace=True)
