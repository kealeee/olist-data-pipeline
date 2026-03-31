{{
    config(
        materialized='incremental',
        unique_key='order_id',
        on_schema_change='fail'
    )
}}

with filtered_data as (
    SELECT
        oi.order_id,
        oi.product_id,
        oi.seller_id,
        o.customer_id,
        o.order_purchase_timestamp::timestamp AS purchased_at,
        oi.price,
        oi.freight_value,
        -- DERIVED COLUMN: Total sale amount for this item
        (oi.price + oi.freight_value) AS total_sale_amount
    FROM {{ source('raw', 'raw_olist_order_items') }} oi
    JOIN {{ source('raw', 'raw_olist_orders') }} o ON oi.order_id = o.order_id
    
    -- DATA QUALITY FILTER: Applying logic from your Great Expectations failure
    WHERE oi.price > 0 
      AND oi.order_id IS NOT NULL

    -- INCREMENTAL LOGIC: Only process orders newer than the last run
    {% if is_incremental() %}
      AND o.order_purchase_timestamp::timestamp > (select max(purchased_at) from {{ this }})
    {% endif %}
)

select * from filtered_data
