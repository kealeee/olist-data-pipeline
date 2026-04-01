{{ config(materialized='view') }}

WITH ranked_reviews AS (
    SELECT
        review_id,
        order_id,
        review_score,
        -- Handle null comments
        COALESCE(review_comment_title, 'No Title') as review_title,
        COALESCE(review_comment_message, 'No Message') as review_message,
        review_creation_date::timestamp as review_created_at,
        review_answer_timestamp::timestamp as review_answered_at,
        -- Deduplication logic
        ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY review_creation_date DESC) as rn
    -- Changed from raw_olist_order_reviews to match your Python script name
    FROM {{ source('raw', 'raw_olist_reviews') }} 
)

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
