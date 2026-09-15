

  create or replace view `dwh`.`int_payments_success` 
  
    
  
  
    
    
  as (
    

SELECT *
FROM `dwh`.`stg_payments`
WHERE status = 'success'
    
  )
      
      
                    -- end_of_sql
                    
                    