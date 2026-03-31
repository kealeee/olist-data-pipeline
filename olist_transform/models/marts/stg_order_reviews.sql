{{ config(materialized='view') }}

WITH ranked_reviews AS (
    SELECT
        review_id,
        order_id,
        review_score,
        -- Handle null comments to prevent downstream errors
        COALESCE(review_comment_title, 'No Title') as review_title,
        COALESCE(review_comment_message, 'No Message') as review_message,
        review_creation_date::timestamp as review_created_at,
        review_answer_timestamp::timestamp as review_answered_at,
        -- Create the row number for deduplication
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC) as rn
    FROM {{ source('raw', 'raw_olist_order_reviews') }}
)

-- Only keep the most recent review per order
SELECT 
    review_id,
    order_id,
    review_score,
    review_title,
    review_message,
    review_created_at,
    review_answered_at
FROM ranked_reviews
WHERE rn = 1
