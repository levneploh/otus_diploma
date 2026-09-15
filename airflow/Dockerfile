FROM apache/airflow:3.3.1

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

USER airflow
RUN pip install --no-cache-dir \
    "apache-airflow-providers-clickhousedb" \
    "apache-airflow-providers-postgres" \
    "apache-airflow-providers-mysql" \
    "apache-airflow-providers-apache-kafka" \
    "apache-airflow-providers-amazon" \
    "dbt-clickhouse" \
    "pandas" \
    "pyarrow"

