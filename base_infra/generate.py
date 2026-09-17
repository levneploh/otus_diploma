#!/usr/bin/env python3
"""
Synthetic data generator for the Avito-like DWH diploma project.

Generates ~2 years of history and loads it into:
  - PostgreSQL (marketplace): users, listings, payments
  - Kafka (user_activity): activity events

Reads dictionary IDs (categories, vas_types) from MySQL (dicts).

Usage:
  container:  docker compose --profile seed run --rm generator
  host:       pip install -r requirements.txt && python generate.py

Volumes and connection settings are configurable via env vars (see README.md).
"""

import datetime as dt
import json
import os
import random
import time
import uuid

import psycopg2
import psycopg2.extras
import pymysql
from confluent_kafka import Producer
from confluent_kafka.admin import AdminClient


# --- Configuration (env vars with defaults) ---------------------------------
def _env_int(name, default):
    return int(os.environ.get(name, default))


PG_HOST = os.environ.get("PG_HOST", "localhost")
PG_PORT = _env_int("PG_PORT", 5432)
PG_USER = os.environ.get("PG_USER", "app")
PG_PASSWORD = os.environ.get("PG_PASSWORD", "app")
PG_DB = os.environ.get("PG_DB", "marketplace")

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = _env_int("MYSQL_PORT", 3306)
MYSQL_USER = os.environ.get("MYSQL_USER", "app")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "app")
MYSQL_DB = os.environ.get("MYSQL_DB", "dict")

KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_TOPIC = os.environ.get("KAFKA_TOPIC", "user_activity")

N_USERS = _env_int("N_USERS", 50_000)
N_LISTINGS = _env_int("N_LISTINGS", 400_000)
N_PAYMENTS = _env_int("N_PAYMENTS", 250_000)
N_EVENTS = _env_int("N_EVENTS", 7_000_000)
YEARS = _env_int("YEARS", 2)

SEED = _env_int("SEED", 42)
BATCH = _env_int("BATCH", 5_000)

END_DATE = dt.datetime.now(dt.timezone.utc)
START_DATE = END_DATE - dt.timedelta(days=365 * YEARS)

random.seed(SEED)

PLATFORMS = ["web", "mweb", "ios", "android"]
PLATFORM_WEIGHTS = [0.45, 0.20, 0.20, 0.15]

LISTING_STATUSES = ["active", "inactive", "sold", "deactivated"]
LISTING_STATUS_WEIGHTS = [0.55, 0.10, 0.30, 0.05]

EVENT_TYPES = ["page_view", "listing_view", "search", "login"]
EVENT_TYPE_WEIGHTS = [0.60, 0.25, 0.10, 0.05]

PAYMENT_TYPES = ["vas", "listing", "subscription"]
PAYMENT_TYPE_WEIGHTS = [0.55, 0.35, 0.10]
PAYMENT_STATUSES = ["success", "failed", "refunded"]
PAYMENT_STATUS_WEIGHTS = [0.95, 0.04, 0.01]

# Prices are in arbitrary units (e.g. rubles).
VAS_PRICES = {1: 150, 2: 1000, 3: 500, 4: 300, 5: 200}
LISTING_FEE_RANGE = (50, 200)
SUBSCRIPTION_FEE_RANGE = (500, 1500)

# Popularity weights for categories (default 1 for parents).
CATEGORY_WEIGHTS = {2: 3, 3: 2, 5: 4, 6: 2, 8: 5, 9: 4, 10: 3, 12: 2, 13: 3}


# --- Helpers ----------------------------------------------------------------
def random_dt(start, end, growth=2.0):
    """Random timestamp in [start, end], biased toward end (growth)."""
    total = (end - start).total_seconds()
    t = random.random() ** (1.0 / growth)
    return start + dt.timedelta(seconds=total * t)


def random_price():
    """Log-uniform price in [~100, ~3.2M]."""
    return round(10 ** random.uniform(2, 6.5), 2)


def wait_for(connect, name, retries=20, delay=3):
    for attempt in range(retries):
        try:
            return connect()
        except Exception as exc:  # noqa: BLE001
            print(f"[{name}] waiting ({attempt + 1}/{retries}): {exc}")
            time.sleep(delay)
    raise RuntimeError(f"{name} is not available")


# --- Connections ------------------------------------------------------------
def connect_pg():
    return psycopg2.connect(
        host=PG_HOST, port=PG_PORT, user=PG_USER, password=PG_PASSWORD, dbname=PG_DB
    )


def connect_mysql():
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB
    )


def wait_for_kafka():
    admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
    for attempt in range(20):
        try:
            admin.list_topics(timeout=5)
            return
        except Exception as exc:  # noqa: BLE001
            print(f"[kafka] waiting ({attempt + 1}/20): {exc}")
            time.sleep(3)
    raise RuntimeError("Kafka is not available")


# --- Generation -------------------------------------------------------------
def read_dicts(mysql_conn):
    cur = mysql_conn.cursor()
    cur.execute("SELECT category_id FROM categories ORDER BY category_id")
    category_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT vas_type_id FROM vas_types ORDER BY vas_type_id")
    vas_type_ids = [r[0] for r in cur.fetchall()]
    cur.close()
    return category_ids, vas_type_ids


def gen_users():
    print(f"[users] generating {N_USERS} ...")
    rows = []
    for i in range(1, N_USERS + 1):
        email = f"user{i}@example.com"
        phone = f"+1{i:010d}" if random.random() < 0.7 else None
        status = random.choices(["active", "blocked", "deleted"], weights=[0.95, 0.04, 0.01])[0]
        registered_at = random_dt(START_DATE, END_DATE)
        rows.append((email, phone, status, registered_at))
    return rows


def gen_listings(category_ids):
    print(f"[listings] generating {N_LISTINGS} ...")
    weights = [CATEGORY_WEIGHTS.get(c, 1) for c in category_ids]
    rows = []
    for i in range(1, N_LISTINGS + 1):
        user_id = random.randint(1, N_USERS)
        category_id = random.choices(category_ids, weights=weights)[0]
        title = f"Listing #{i}"
        price = random_price()
        status = random.choices(LISTING_STATUSES, weights=LISTING_STATUS_WEIGHTS)[0]
        platform = random.choices(PLATFORMS, weights=PLATFORM_WEIGHTS)[0]
        created_at = random_dt(START_DATE, END_DATE)
        activated_at = created_at if status in ("active", "sold", "deactivated") else None
        sold_at = created_at + dt.timedelta(days=random.randint(1, 60)) if status == "sold" else None
        deactivated_at = created_at + dt.timedelta(days=random.randint(30, 365)) if status == "deactivated" else None
        rows.append((user_id, category_id, title, price, status, platform,
                     created_at, activated_at, sold_at, deactivated_at))
    return rows


def gen_payments(vas_type_ids):
    print(f"[payments] generating {N_PAYMENTS} ...")
    rows = []
    for _ in range(N_PAYMENTS):
        ptype = random.choices(PAYMENT_TYPES, weights=PAYMENT_TYPE_WEIGHTS)[0]
        status = random.choices(PAYMENT_STATUSES, weights=PAYMENT_STATUS_WEIGHTS)[0]
        payment_date = random_dt(START_DATE, END_DATE)
        if ptype in ("vas", "listing"):
            listing_id = random.randint(1, N_LISTINGS)
            user_id = random.randint(1, N_USERS)
            if ptype == "vas":
                vas_type_id = random.choice(vas_type_ids)
                amount = VAS_PRICES[vas_type_id]
            else:
                vas_type_id = None
                amount = random.randint(*LISTING_FEE_RANGE)
        else:  # subscription
            user_id = random.randint(1, N_USERS)
            listing_id = None
            vas_type_id = None
            amount = random.randint(*SUBSCRIPTION_FEE_RANGE)
        rows.append((user_id, listing_id, vas_type_id, amount, ptype, status, payment_date))
    return rows


def daily_event_counts():
    total_days = (END_DATE - START_DATE).days
    weights = []
    for d in range(total_days):
        date = START_DATE + dt.timedelta(days=d)
        growth = 0.5 + (d / max(total_days - 1, 1))
        season = 0.7 if date.weekday() >= 5 else 1.0
        weights.append(growth * season)
    total = sum(weights)
    counts = [int(N_EVENTS * w / total) for w in weights]
    counts[-1] += N_EVENTS - sum(counts)
    return counts


def gen_events(producer):
    print(f"[events] generating {N_EVENTS} ...")
    flush_every = 100_000
    counts = daily_event_counts()
    produced = 0
    for d, count in enumerate(counts):
        date = START_DATE + dt.timedelta(days=d)
        for _ in range(count):
            user_id = random.randint(1, N_USERS)
            event_type = random.choices(EVENT_TYPES, weights=EVENT_TYPE_WEIGHTS)[0]
            platform = random.choices(PLATFORMS, weights=PLATFORM_WEIGHTS)[0]
            listing_id = random.randint(1, N_LISTINGS) if event_type == "listing_view" else None
            ts = date + dt.timedelta(seconds=random.randint(0, 86399))
            event = {
                "event_id": str(uuid.uuid4()),
                "user_id": user_id,
                "event_type": event_type,
                "platform": platform,
                "listing_id": listing_id,
                "session_id": uuid.uuid4().hex,
                "ts": ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
            }
            producer.produce(KAFKA_TOPIC, key=str(user_id), value=json.dumps(event))
            produced += 1
            if produced % flush_every == 0:
                producer.flush()
                print(f"[events] produced {produced}/{N_EVENTS}")
    producer.flush()
    print(f"[events] done: {produced} messages")


# --- Inserts -----------------------------------------------------------------
def insert_users(pg_conn, rows):
    cur = pg_conn.cursor()
    sql = "INSERT INTO users (email, phone, status, registered_at) VALUES %s"
    for i in range(0, len(rows), BATCH):
        psycopg2.extras.execute_values(cur, sql, rows[i:i + BATCH])
        pg_conn.commit()
        print(f"[users] inserted {min(i + BATCH, len(rows))}/{len(rows)}")
    cur.close()


def insert_listings(pg_conn, rows):
    cur = pg_conn.cursor()
    sql = ("INSERT INTO listings (user_id, category_id, title, price, status, platform, "
           "created_at, activated_at, sold_at, deactivated_at) VALUES %s")
    for i in range(0, len(rows), BATCH):
        psycopg2.extras.execute_values(cur, sql, rows[i:i + BATCH])
        pg_conn.commit()
        print(f"[listings] inserted {min(i + BATCH, len(rows))}/{len(rows)}")
    cur.close()


def insert_payments(pg_conn, rows):
    cur = pg_conn.cursor()
    sql = ("INSERT INTO payments (user_id, listing_id, vas_type_id, amount, payment_type, status, payment_date) "
           "VALUES %s")
    for i in range(0, len(rows), BATCH):
        psycopg2.extras.execute_values(cur, sql, rows[i:i + BATCH])
        pg_conn.commit()
        print(f"[payments] inserted {min(i + BATCH, len(rows))}/{len(rows)}")
    cur.close()


def truncate_tables(pg_conn):
    cur = pg_conn.cursor()
    cur.execute("TRUNCATE TABLE users, listings, payments RESTART IDENTITY CASCADE")
    pg_conn.commit()
    cur.close()
    print("[reset] truncated users, listings, payments")


# --- Main --------------------------------------------------------------------
def main():
    pg = wait_for(connect_pg, "postgres")
    mysql = wait_for(connect_mysql, "mysql")
    wait_for_kafka()

    category_ids, vas_type_ids = read_dicts(mysql)
    print(f"[dicts] categories={len(category_ids)}, vas_types={len(vas_type_ids)}")

    truncate_tables(pg)

    insert_users(pg, gen_users())
    insert_listings(pg, gen_listings(category_ids))
    insert_payments(pg, gen_payments(vas_type_ids))

    producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP, "linger.ms": 10})
    gen_events(producer)

    pg.close()
    mysql.close()
    print("done.")


if __name__ == "__main__":
    main()

