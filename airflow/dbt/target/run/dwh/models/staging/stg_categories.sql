

  create or replace view `dwh`.`stg_categories` 
  
    
  
  
    
    
  as (
    

SELECT
    category_id,
    name,
    parent_id
FROM s3(
    'http://minio:9000/raw/mysql/categories/*.parquet',
    'Parquet',
    'category_id Int32, name String, parent_id Nullable(Int32)'
)
    
  )
      
      
                    -- end_of_sql
                    
                    