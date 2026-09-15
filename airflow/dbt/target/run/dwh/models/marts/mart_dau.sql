
  
    
    
    
        


        
  

  insert into `dwh`.`mart_dau`
        ("day", "platform", "dau")

SELECT
    toDate(ts) AS day,
    platform,
    uniqExact(user_id) AS dau
FROM `dwh`.`stg_user_activity`
GROUP BY day, platform
ORDER BY day, platform
  