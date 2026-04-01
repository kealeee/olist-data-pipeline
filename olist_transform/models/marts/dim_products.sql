{{ config(materialized='table') }}

SELECT
    p."product_id",
    COALESCE(t."product_category_name_english", p."product_category_name") AS product_category_name,
    p."product_name_lenght",
    p."product_description_lenght",
    p."product_photos_qty",
    p."product_weight_g",
    p."product_length_cm",
    p."product_height_cm",
    p."product_width_cm"
FROM {{ source('raw', 'raw_olist_products') }} p
LEFT JOIN {{ source('raw', 'raw_product_category_translation') }} t
  ON p."product_category_name" = t."product_category_name"
