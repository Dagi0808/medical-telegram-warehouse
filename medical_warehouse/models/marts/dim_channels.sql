{{ config(materialized='table') }}

with channels as (
    select distinct channel_name
    from {{ ref('stg_telegram_messages') }}
),

stats as (
    select
        channel_name,
        min(message_date) as first_post_date,
        max(message_date) as last_post_date,
        count(*) as total_posts,
        avg(views) as avg_views,
        count(case when has_image then 1 end) as posts_with_image
    from {{ ref('stg_telegram_messages') }}
    group by channel_name
)

select
    row_number() over (order by c.channel_name) as channel_key,
    c.channel_name,
    case 
        when c.channel_name ilike '%chemed%' or c.channel_name ilike '%pharma%' then 'Pharmaceutical'
        when c.channel_name ilike '%lobelia%' or c.channel_name ilike '%cosmetics%' then 'Cosmetics'
        else 'Medical'
    end as channel_type,
    s.first_post_date,
    s.last_post_date,
    s.total_posts,
    s.avg_views,
    s.posts_with_image
from channels c
left join stats s on c.channel_name = s.channel_name
