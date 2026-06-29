{{ config(materialized='view') }}

with source as (
    select * from raw.telegram_messages
),

cleaned as (
    select
        message_id,
        channel_name,
        message_date::timestamp as message_date,
        message_text,
        has_media,
        image_path,
        views,
        forwards,
        length(coalesce(message_text, '')) as message_length,
        case when image_path is not null then true else false end as has_image,
        now() as loaded_at
    from source
    where message_date is not null
)

select * from cleaned
