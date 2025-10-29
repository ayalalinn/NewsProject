import asyncio
import requests
from datetime import datetime
from app.services.kafka import send_to_kafka

KAFKA_TOPIC = "news.raw"

async def send_article_to_kafka(article: dict):
    """שולח כתבה אחת ל־Kafka"""
    await send_to_kafka(KAFKA_TOPIC, article, key=article["external_id"])

async def fetch_from_newsapi(api_key: str, categories: list = ["general", "technology"]):
    """מביא חדשות מה־NewsAPI ושולח כל כתבה ל־Kafka"""
    if not api_key:
        print("❌ שגיאה: NEWS_API_KEY לא מוגדר או ריק.")
        return

    for category in categories:
        try:
            headers = {"X-Api-Key": api_key}
            url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}"
            print(f"🌐 מבצע בקשה ל-NewsAPI ({category})...")

            resp = requests.get(url, headers=headers)
            data = resp.json()

            # בדיקה אם ה־API מחזיר שגיאה
            if data.get("status") != "ok":
                print(f"❌ שגיאה ב-NewsAPI ({category}): {data}")
                continue

            articles = data.get("articles", [])
            print(f"📡 נמצאו {len(articles)} כתבות בקטגוריה {category}")

            # שליחת כל כתבה ל-Kafka
            for item in articles:
                article = {
                    "external_id": item.get("url"),
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "summary": item.get("description"),
                    "category": category,
                    "fetched_at": datetime.utcnow().isoformat(),
                }
                await send_article_to_kafka(article)  # ✅ במקום asyncio.run()
                print(f"✅ נשלחה כתבה: {article['title']}")
        except Exception as e:
            print(f"⚠️ שגיאה בזמן שליפת קטגוריה {category}: {e}")

    print("✅ כל הכתבות נשלחו ל-Kafka")
