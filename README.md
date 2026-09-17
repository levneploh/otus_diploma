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
docker network create lev_diploma_net
mkdir otus
cd otus
git clone git@github.com:levneploh/otus_diploma.git
cd otus_diploma

 
 1 - docker-compose.yaml
  -  здесь живут clickhouse, kafka, postgres, mysql, minio, tools

 2 - отдельно устанавливаем superset и airflow (c драйверами для бд).
 2.1 airflow setup
 cd airflow
 создайте .env файл:
 KEY=$(python3 -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())")
 echo -e "AIRFLOW_UID=$(id -u)" > .env
 echo "FERNET_KEY=${KEY}" >> .env

 docker compose up -d

 2.2 superset
 
 

 3 - заводим таблицы в mysql и pg.
 4 - генерируем тестовые данные 
     docker compose --profile seed run --rm generator
 5 - далее запускаем подряд dags - 
     pg_to_minio → mysql_to_minio → kafka_to_minio → dbt_run
    
 6 - смотрим dashbord @ superset.
