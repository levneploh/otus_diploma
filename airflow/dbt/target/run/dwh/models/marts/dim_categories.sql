
  
    
    
    
        


        
  

  insert into `dwh`.`dim_categories`
        ("category_id", "category_name", "parent_id")

SELECT
    category_id,
    name AS category_name,
    parent_id
FROM `dwh`.`stg_categories`
  