"""Run dbt (transform MinIO Parquet -> ClickHouse marts).

Run this DAG AFTER the ingestion DAGs (pg/mysql/kafka_to_minio).
"""
from datetime import datetime, timezone

from airflow import DAG
from airflow.operators.bash import BashOperator

DBT_DIR = "/opt/airflow/dbt"

with DAG(
    dag_id="dbt_run",
    schedule=None,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["dbt"],
    description="dbt run: staging -> intermediate -> marts in ClickHouse",
) as dag:
    BashOperator(
        task_id="dbt_run",
        bash_command=f"cd {DBT_DIR} && /home/airflow/.local/bin/dbt run",
        env={
            "DBT_PROFILES_DIR": f"{DBT_DIR}/profiles",
            "CLICKHOUSE_HOST": "clickhouse",
            "MINIO_ENDPOINT": "http://minio:9000",
        },
    )
