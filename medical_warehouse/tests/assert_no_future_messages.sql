-- Assert no future messages
select * 
from {{ ref('stg_telegram_messages') }}
where message_date > current_timestamp
limit 1
