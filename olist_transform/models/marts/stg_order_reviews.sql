{{ config(materialized='view') }}

with ranked_reviews as (
    select
        review_id,
        order_id,
        review_score,
        coalesce(review_comment_title, 'No Title') as review_title,
        coalesce(review_comment_message, 'No Message') as review_message,
        review_creation_date::timestamp as review_created_at,
        review_answer_timestamp::timestamp as review_answered_at,
        row_number() over (
            partition by order_id
            order by review_creation_date desc
        ) as rn
    from {{ source('raw', 'raw_olist_reviews') }}  -- ✅ Correct table name
)

select
    review_id,
    order_id,
    review_score,
    review_title,
    review_message,
    review_created_at,
    review_answered_at
from ranked_reviews
where rn = 1