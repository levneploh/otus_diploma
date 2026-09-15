"""Ingestion: MySQL (dicts) -> MinIO (Parquet).

Extracts categories, vas_types and writes them to:
    raw/mysql/<table>/data.parquet
"""
from datetime import datetime, timezone

from airflow import DAG
from airflow.operators.python import PythonOperator

from ingestion_common import read_mysql, write_parquet


def extract_categories():
    write_parquet(read_mysql("categories"), "mysql/categories/data.parquet")


def extract_vas_types():
    write_parquet(read_mysql("vas_types"), "mysql/vas_types/data.parquet")


with DAG(
    dag_id="mysql_to_minio",
    schedule=None,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["ingestion"],
    description="MySQL (dictionaries) -> MinIO raw Parquet",
) as dag:
    t_categories = PythonOperator(task_id="extract_categories", python_callable=extract_categories)
    t_vas_types = PythonOperator(task_id="extract_vas_types", python_callable=extract_vas_types)

    t_categories >> t_vas_types
