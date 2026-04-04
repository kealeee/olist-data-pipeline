
  
    

  create  table "olist_dw"."analytics"."dim_customers__dbt_tmp"
  
  
    as
  
  (
    

select
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
from "olist_dw"."raw"."raw_olist_customers"
  );
  