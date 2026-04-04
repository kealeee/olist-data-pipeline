
  
    

  create  table "olist_dw"."analytics"."dim_products__dbt_tmp"
  
  
    as
  
  (
    

select
    p.product_id,
    coalesce(t.product_category_name_english, p.product_category_name) as product_category_name,
    p.product_name_lenght,
    p.product_description_lenght,
    p.product_photos_qty,
    p.product_weight_g,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm
from "olist_dw"."raw"."raw_olist_products" p
left join "olist_dw"."raw"."raw_product_category_translation" t
  on p.product_category_name = t.product_category_name
  );
  