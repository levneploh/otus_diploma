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

 
 1 - docker-compose.yaml
  -  здесь живут clickhouse, kafka, postgres, mysql, minio, tools

 2 - отдельно устанавливаем superset и airflow (c драйверами для бд).

 3 - заводим таблицы в mysql и pg.
 4 - генерируем тестовые данные 
     docker compose --profile seed run --rm generator
 5 - далее запускаем подряд dags - 
     pg_to_minio → mysql_to_minio → kafka_to_minio → dbt_run
    
 6 - смотрим dashbord @ superset.
