{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'
) }}

with filtered_data as (
    select
        oi.order_id,
        oi.product_id,
        oi.seller_id,
        o.customer_id,
        o.order_purchase_timestamp::timestamp as purchased_at,
        oi.price,
        oi.freight_value,
        (oi.price + oi.freight_value) as total_sale_amount
    from {{ source('raw', 'raw_olist_order_items') }} oi
    join {{ source('raw', 'raw_olist_orders') }} o
      on oi.order_id = o.order_id
    where oi.price > 0
      and oi.order_id is not null
    {% if is_incremental() %}
      and o.order_purchase_timestamp::timestamp > (
          select max(purchased_at) from {{ this }}
      )
    {% endif %}
)

select * from filtered_data
