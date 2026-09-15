

  create or replace view `dwh`.`stg_user_activity` 
  
    
  
  
    
    
  as (
    

SELECT
    event_id,
    user_id,
    event_type,
    platform,
    listing_id,
    session_id,
    ts
FROM s3(
    'http://minio:9000/raw/kafka/user_activity/*.parquet',
    'Parquet',
    'event_id String, user_id Int64, event_type String, platform String, listing_id Nullable(Int64), session_id String, ts DateTime64(3)'
)
    
  )
      
      
                    -- end_of_sql
                    
                    