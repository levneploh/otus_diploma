
  
    
    
    
        


        
  

  insert into `dwh`.`mart_revenue_daily`
        ("day", "revenue")

SELECT
    toDate(payment_date) AS day,
    sum(amount) AS revenue
FROM `dwh`.`int_payments_success`
GROUP BY day
ORDER BY day
  