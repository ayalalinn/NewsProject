import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from app.services.collector import fetch_from_newsapi

# טוען משתני סביבה רק פעם אחת
load_dotenv()

async def periodic_news_fetch(interval_sec=60):
    """מביא חדשות כל X שניות ומעביר אותן ל-Kafka"""
    while True:
        newsapi_key = os.getenv("NEWS_API_KEY")

        if not newsapi_key:
            print("❌ שגיאה: NEWS_API_KEY לא מוגדר או ריק.")
        else:
            print(f"🕒 בודק עדכונים חדשים... {datetime.utcnow().isoformat()}")
            await fetch_from_newsapi(newsapi_key, categories=["general", "technology", "business"])

        await asyncio.sleep(interval_sec)
