"""Ingestion: Kafka (user_activity) -> MinIO (Parquet).

Consumes activity events in batches and writes them to:
    raw/kafka/user_activity/part-XXXXX.parquet
"""
import json
from datetime import datetime, timezone

import pandas as pd
from airflow import DAG
from airflow.operators.python import PythonOperator
from confluent_kafka import Consumer

from ingestion_common import KAFKA_BOOTSTRAP, KAFKA_TOPIC, write_parquet

BATCH_SIZE = 200_000


def _write_batch(records: list, part: int) -> None:
    df = pd.DataFrame(records)
    df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_localize(None)
    if "listing_id" in df.columns:
        df["listing_id"] = pd.to_numeric(df["listing_id"], errors="coerce").astype("Int64")
    write_parquet(df, f"kafka/user_activity/part-{part:05d}.parquet")


def consume_kafka():
    consumer = Consumer({
        "bootstrap.servers": KAFKA_BOOTSTRAP,
        "group.id": "airflow_ingestion",
        "auto.offset.reset": "earliest",
        "enable.auto.commit": True,
    })
    consumer.subscribe([KAFKA_TOPIC])

    batch = []
    part = 0
    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                break
            if msg.error():
                continue
            batch.append(json.loads(msg.value().decode("utf-8")))
            if len(batch) >= BATCH_SIZE:
                _write_batch(batch, part)
                part += 1
                batch = []
    finally:
        consumer.close()

    if batch:
        _write_batch(batch, part)


with DAG(
    dag_id="kafka_to_minio",
    schedule=None,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["ingestion"],
    description="Kafka (events) -> MinIO raw Parquet",
) as dag:
    PythonOperator(task_id="consume_user_activity", python_callable=consume_kafka)
