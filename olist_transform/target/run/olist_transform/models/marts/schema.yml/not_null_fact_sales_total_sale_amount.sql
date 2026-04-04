
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_sale_amount
from "olist_dw"."analytics"."fact_sales"
where total_sale_amount is null



  
  
      
    ) dbt_internal_test