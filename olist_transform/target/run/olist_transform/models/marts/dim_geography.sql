
  
    

  create  table "olist_dw"."analytics"."dim_geography__dbt_tmp"
  
  
    as
  
  (
    

with base_geography as (
    select distinct
        geolocation_zip_code_prefix as zip_code_prefix,
        geolocation_city as city,
        geolocation_state as state_code
    from "olist_dw"."raw"."raw_olist_geolocation"
)

select
    zip_code_prefix,
    city,
    state_code,
    case
        when state_code in ('AC','AM','AP','PA','RO','RR','TO') then 'North'
        when state_code in ('AL','BA','CE','MA','PB','PE','PI','RN','SE') then 'Northeast'
        when state_code in ('DF','GO','MT','MS') then 'Central-West'
        when state_code in ('ES','MG','RJ','SP') then 'Southeast'
        when state_code in ('PR','RS','SC') then 'South'
        else 'Unknown'
    end as macro_region
from base_geography
  );
  