{{ config(materialized='table') }}

select
    m.message_id,
    c.channel_key,
    d.date_key,
    m.message_text,
    m.message_length,
    m.views,
    m.forwards,
    m.has_image
from {{ ref('stg_telegram_messages') }} m
left join {{ ref('dim_channels') }} c on m.channel_name = c.channel_name
left join {{ ref('dim_dates') }} d on date(m.message_date) = d.full_date
