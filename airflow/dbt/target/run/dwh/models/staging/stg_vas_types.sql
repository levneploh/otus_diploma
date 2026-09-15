

  create or replace view `dwh`.`stg_vas_types` 
  
    
  
  
    
    
  as (
    

SELECT
    vas_type_id,
    name,
    description
FROM s3(
    'http://minio:9000/raw/mysql/vas_types/*.parquet',
    'Parquet',
    'vas_type_id Int32, name String, description Nullable(String)'
)
    
  )
      
      
                    -- end_of_sql
                    
                    