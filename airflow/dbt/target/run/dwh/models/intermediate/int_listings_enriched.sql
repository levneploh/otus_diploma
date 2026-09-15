

  create or replace view `dwh`.`int_listings_enriched` 
  
    
  
  
    
    
  as (
    

SELECT
    l.listing_id,
    l.user_id,
    l.category_id,
    c.name AS category_name,
    l.title,
    l.price,
    l.status,
    l.platform,
    l.created_at,
    l.sold_at
FROM `dwh`.`stg_listings` l
LEFT JOIN `dwh`.`stg_categories` c ON l.category_id = c.category_id
    
  )
      
      
                    -- end_of_sql
                    
                    