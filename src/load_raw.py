
import json
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def load_to_postgres():
    conn = psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB'),
        user=os.getenv('POSTGRES_USER'),
        password=os.getenv('POSTGRES_PASSWORD'),
        host=os.getenv('POSTGRES_HOST')
    )
    cur = conn.cursor()
    
    # Create schema and table
    cur.execute("""
        CREATE SCHEMA IF NOT EXISTS raw;
        DROP TABLE IF EXISTS raw.telegram_messages;
        CREATE TABLE raw.telegram_messages (
            message_id BIGINT PRIMARY KEY,
            channel_name TEXT,
            message_date TIMESTAMP,
            message_text TEXT,
            has_media BOOLEAN,
            image_path TEXT,
            views INTEGER,
            forwards INTEGER,
            loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Load all JSON files
    loaded_count = 0
    for root, dirs, files in os.walk('data/raw/telegram_messages'):
        for file in files:
            if file.endswith('.json'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                values = []
                for msg in data:
                    values.append((
                        msg.get('message_id'),
                        msg.get('channel_name'),
                        msg.get('message_date'),
                        msg.get('message_text'),
                        msg.get('has_media'),
                        msg.get('image_path'),
                        msg.get('views'),
                        msg.get('forwards')
                    ))
                
                if values:
                    execute_values(cur, """
                        INSERT INTO raw.telegram_messages 
                        (message_id, channel_name, message_date, message_text, has_media, image_path, views, forwards)
                        VALUES %s
                        ON CONFLICT (message_id) DO NOTHING
                    """, values)
                    loaded_count += len(values)
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Loaded {loaded_count} messages into PostgreSQL raw schema.")

if __name__ == "__main__":
    load_to_postgres()
