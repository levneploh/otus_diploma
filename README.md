# otus_diploma
Дипломная работа по курсу DWH Analyst.

Собираем примерную структуру сервиса размещения обьявлений (avito, youla like).

 ### Инфраструктура - 

 Источники 
 - PostgreSql ( основная база с пользователями и обьявлениями)
 - Mysql - справочная база (категории, типы "поднятий")
 - Kafka - активность пользователей.

 Оркестрация - 
 Данные из источников отправляются в DataLake на базе Minio и сохраняются в формате parquet.
 Далее через DBT данные трансформируются и заливаются (tables and views) в Clickhouse.

 BI система на базе Superset 

 ### Setup 

создаем общую сеть для всех compose
```
docker network create lev_diploma_net
```

```
mkdir otus
cd otus
git clone git@github.com:levneploh/otus_diploma.git
cd otus_diploma

```


```
.
├── airflow
├── base_infra
├── README.md
└── superset

```

### base_infra
 
  -  здесь живут clickhouse, kafka, postgres, mysql, minio, tools
просто поднимаем через docker compose

```
cd base_infra
# или используем .env из примера, или задаем свой
cp env.example .env
docker compose up -d
```


отдельно устанавливаем superset и airflow

### airflow
```
cd airflow
```

###### создайте .env файл:

```

KEY=$(python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())")
echo -e "AIRFLOW_UID=$(id -u)" > .env
echo "FERNET_KEY=${KEY}" >> .env
```

```
docker compose up -d
```
 

 ### superset

 клонируем репо вне текущей директории, например ~/Desktop/lev-superset
```
mkdir ~/Desktop/lev-superset
```

 ```
 git clone --depth 1 --branch 6.1.0 https://github.com/apache/superset.git ~/Desktop/lev-superset
 ```


кладем кастомный dockerfile и docker-compose
```
mkdir ~/Desktop/lev-superset/custom
cp superset-files/Dockerfile ~/Desktop/lev-superset/custom
cp superset-files/docker-compose-non-dev.yml ~/Desktop/lev-superset/docker-compose-non-dev.yml
```

отключить загрузку примеров
```
в файле ~/Desktop/lev-superset/docker/.env
выставить 
SUPERSET_LOAD_EXAMPLES=no
```

```
cd ~/Desktop/lev-superset
```

собрать - 
```
docker compose -f docker-compose-non-dev.yml build
```

 запустить
 ```
 docker compose -f docker-compose-non-dev.yml up -d
 ```



запускаем генератор данных из директории base_infra
```
docker compose --profile seed build generator
docker compose --profile seed run --rm generator
```


### создаем коннекты в airflow 
подтягиваем пароли - 
```
source base_infra/.env

```

```
cd airflow

```


```
docker compose exec airflow-scheduler airflow connections add postgres_source \
  --conn-type postgres --conn-host postgres --conn-login dbuser \
  --conn-password "${POSTGRES_PASSWORD}" --conn-port 5432 --conn-schema marketplace

docker compose exec airflow-scheduler airflow connections add mysql_source \
  --conn-type mysql --conn-host mysql --conn-login app \
  --conn-password "${MYSQL_PASSWORD}" --conn-port 3306 --conn-schema dict

docker compose exec airflow-scheduler airflow connections add minio \
  --conn-type aws --conn-login "${MINIO_ROOT_USER}" \
  --conn-password "${MINIO_ROOT_PASSWORD}" \
  --conn-extra '{"endpoint_url": "http://minio:9000"}'
```
 
 
### запустить  DAG'и
 pg_to_minio → mysql_to_minio → kafka_to_minio → dbt_run.
 
 
 импортируем через web dashboard в superset (admin:admin)
```
superset-files/dashboard_export_20260917T222708.zip
```




