# dbt-проект (lakehouse)

Трансформационный слой `staging → intermediate → marts` в ClickHouse.
Staging-модели читают сырые данные (Parquet) напрямую из MinIO через `s3()`.

## Запуск

```bash
cd dbt
export DBT_PROFILES_DIR=./profiles
dbt run
dbt test
dbt docs generate
```

## Структура

```
dbt/
├── dbt_project.yml
├── profiles/profiles.yml
└── models/
    ├── staging/        # stg_* — view поверх s3() (Parquet в MinIO)
    ├── intermediate/   # int_* — join'ы, очистка
    └── marts/          # dim_*, mart_* — витрины (5 шт)
```

## Витрины (5)

| Модель | Что показывает |
|---|---|
| `mart_listings_by_category` | объявления по категориям |
| `mart_dau` | DAU по платформам |
| `mart_revenue_daily` / `mart_revenue_monthly_yoy` | выручка по периодам + YoY |
| `mart_vas` | VAS metrics |
| `mart_arpu_monthly` | ARPU = выручка / MAU |

## Конфигурация (env)

- `MINIO_ENDPOINT` — адрес MinIO (по умолчанию `http://localhost:9000`)
- `CLICKHOUSE_HOST` / `CLICKHOUSE_USER` / `CLICKHOUSE_PASSWORD` — подключение к ClickHouse
