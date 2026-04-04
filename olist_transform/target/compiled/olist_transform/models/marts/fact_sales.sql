

with filtered_data as (
    select
        oi.order_id,       -- 👈 ADD THIS LINE HERE
        oi.order_item_id,  
        oi.product_id,
        oi.seller_id,
        o.customer_id,  
        o.order_purchase_timestamp::timestamp as purchased_at,
        oi.price,
        oi.freight_value,
        (oi.price + oi.freight_value) as total_sale_amount
    from "olist_dw"."raw"."raw_olist_order_items" oi
    join "olist_dw"."raw"."raw_olist_orders" o
      on oi.order_id = o.order_id
    where oi.price > 0
      and oi.order_id is not null
    
      and o.order_purchase_timestamp::timestamp > (
          select max(purchased_at) from "olist_dw"."analytics"."fact_sales"
      )
    
)

select * from filtered_data