{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='fail'
    )
}}

WITH filtered_data AS (
    SELECT
        oi.order_id,
        oi.product_id,
        oi.seller_id,
        o.customer_id,
        o.order_purchase_timestamp::timestamp AS purchased_at,
        oi.price,
        oi.freight_value,
        (oi.price + oi.freight_value) AS total_sale_amount
    FROM {{ source('raw', 'raw_olist_order_items') }} oi
    JOIN {{ source('raw', 'raw_olist_orders') }} o 
      ON oi.order_id = o.order_id
    
    WHERE oi.price > 0 
      AND oi.order_id IS NOT NULL

    {% if is_incremental() %}
      -- This ensures we only pull new data during incremental runs
      AND o.order_purchase_timestamp::timestamp > (SELECT max(purchased_at) FROM {{ this }})
    {% endif %}
)

SELECT * FROM filtered_data
