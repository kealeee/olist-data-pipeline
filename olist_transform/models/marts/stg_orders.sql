{{ config(
    materialized='view'
) }}

WITH source AS (
    SELECT * 
    FROM {{ source('raw', 'raw_olist_orders') }}
)

SELECT
    order_id,
    customer_id,
    order_status,
    
    -- Timestamps
    order_purchase_timestamp::TIMESTAMP AS order_purchase_timestamp,
    order_approved_at::TIMESTAMP AS order_approved_at,
    order_delivered_carrier_date::TIMESTAMP AS order_delivered_carrier_date,
    order_delivered_customer_date::TIMESTAMP AS order_delivered_customer_date,
    order_estimated_delivery_date::TIMESTAMP AS order_estimated_delivery_date,

    -- Optional useful derived columns
    CASE 
        WHEN order_delivered_customer_date IS NOT NULL 
        THEN DATE_PART('day', order_delivered_customer_date::TIMESTAMP - order_purchase_timestamp::TIMESTAMP)
    END AS actual_delivery_days,

    CASE 
        WHEN order_delivered_customer_date IS NOT NULL AND order_estimated_delivery_date IS NOT NULL
        THEN DATE_PART('day', order_delivered_customer_date::TIMESTAMP - order_estimated_delivery_date::TIMESTAMP)
    END AS delivery_delay_days   -- Positive = Late, Negative = Early

FROM source