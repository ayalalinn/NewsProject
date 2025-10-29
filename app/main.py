import os
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import gradio as gr

from app.services.kafka import send_to_kafka
from app.services.collector import fetch_from_newsapi
from app.services.scheduler import periodic_news_fetch
from app.routers.articles import router as articles_router
from app.routers.webhooks import router as webhooks_router
from app.ui import build_ui



# === טעינת משתני סביבה ===
load_dotenv()  # טוען את הקובץ .env
print("🔑 Loaded NEWS_API_KEY:", os.getenv("NEWS_API_KEY"))

# === יצירת האפליקציה ===
app = FastAPI(title="NewsProject - Article View (MVC)")

# חיבור ה־routers
app.include_router(articles_router)
app.include_router(webhooks_router, prefix="/webhooks")

# === הגדרת CORS (פתוח לפיתוח, בפרודקשן כדאי להגביל) ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === נתיב בדיקה ===
@app.get("/api/health")
def health():
    return {"status": "ok"}

# === שילוב ממשק המשתמש (Gradio) ===
gradio_app = build_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/article")

# === הפעלת Scheduler + שאיבת חדשות אוטומטית ===
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(periodic_news_fetch(interval_sec=60))

