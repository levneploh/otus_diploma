
  
    
    
    
        


        
  

  insert into `dwh`.`dim_vas_types`
        ("vas_type_id", "vas_type_name", "description")

SELECT
    vas_type_id,
    name AS vas_type_name,
    description
FROM `dwh`.`stg_vas_types`
  