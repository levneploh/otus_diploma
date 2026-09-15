"""Ingestion: PostgreSQL (marketplace) -> MinIO (Parquet).

Extracts users, listings, payments and writes them to:
    raw/postgres/<table>/data.parquet
"""
from datetime import datetime, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion_common import cast_float, read_postgres, write_parquet


def extract_users():
    write_parquet(read_postgres("users"), "postgres/users/data.parquet")


def extract_listings():
    df = read_postgres("listings")
    df = cast_float(df, ["price"])
    write_parquet(df, "postgres/listings/data.parquet")


def extract_payments():
    df = read_postgres("payments")
    df = cast_float(df, ["amount"])
    write_parquet(df, "postgres/payments/data.parquet")


with DAG(
    dag_id="pg_to_minio",
    schedule=None,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["ingestion"],
    description="PostgreSQL (core) -> MinIO raw Parquet",
) as dag:
    t_users = PythonOperator(task_id="extract_users", python_callable=extract_users)
    t_listings = PythonOperator(task_id="extract_listings", python_callable=extract_listings)
    t_payments = PythonOperator(task_id="extract_payments", python_callable=extract_payments)

    [t_users, t_listings, t_payments]
