import os
import json
import logging
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto
from dotenv import load_dotenv
import asyncio

load_dotenv()

os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/scraper.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

API_ID = int(os.getenv('TELEGRAM_API_ID'))
API_HASH = os.getenv('TELEGRAM_API_HASH')

async def scrape_channel(client, channel_username, limit=30):
    try:
        entity = await client.get_entity(channel_username)
        print(f"✅ Scraping: {channel_username}")
        
        messages = []
        count = 0
        
        async for message in client.iter_messages(entity, limit=limit):
            msg_data = {
                'message_id': message.id,
                'channel_name': channel_username,
                'message_date': message.date.isoformat() if message.date else None,
                'message_text': message.message,
                'has_media': message.media is not None,
                'views': getattr(message, 'views', 0),
                'forwards': getattr(message, 'forwards', 0),
            }
            
            if isinstance(message.media, MessageMediaPhoto):
                path = f"data/raw/images/{channel_username}/{message.id}.jpg"
                os.makedirs(os.path.dirname(path), exist_ok=True)
                await message.download_media(path)
                msg_data['image_path'] = path
            
            messages.append(msg_data)
            count += 1
            if count % 10 == 0:
                print(f"   → {count} messages from {channel_username}")
        
        # Save
        date_str = datetime.now().strftime('%Y-%m-%d')
        os.makedirs(f"data/raw/telegram_messages/{date_str}", exist_ok=True)
        filepath = f"data/raw/telegram_messages/{date_str}/{channel_username.replace('@', '')}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {len(messages)} messages from {channel_username}\n")
        
    except Exception as e:
        print(f"❌ Error scraping {channel_username}: {e}")

async def main():
    async with TelegramClient('telegram_session', API_ID, API_HASH) as client:
        channels = [
            '@CheMed123',
            'lobelia_cosmetics',
            'tikvahpharma',
            # Add more real ones you find
        ]
        
        for ch in channels:
            await scrape_channel(client, ch, limit=30)
            await asyncio.sleep(2)  # Small delay between channels

if __name__ == "__main__":
    print("🚀 Starting Telegram Scraper...")
    asyncio.run(main())
