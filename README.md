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
cp .env.example .env
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

 клонируем репо 
 ```
 git clone --depth 1 --branch 6.1.0 https://github.com/apache/superset.git
 ```


кладем кастомный dockerfile и docker-compose
```
mkdir superset/custom
cp superset-files/Dockerfile superset/custom/
cp superset-files/docker-compose-non-dev.yml superset/docker-compose-non-dev.yml
```

отключить загрузку примеров
```
в файле superset/docker/.env
выставить 
SUPERSET_LOAD_EXAMPLES=no
```

собрать - 
```
docker compose -f docker-compose-non-dev.yml build
```

 запустить
 ```
 docker compose -f docker-compose-non-dev.yml up -d
 ```

 
 4 - генерируем тестовые данные 
     docker compose --profile seed run --rm generator
 5 - далее запускаем подряд dags - 
     pg_to_minio → mysql_to_minio → kafka_to_minio → dbt_run
    
 6 - смотрим dashbord @ superset.
