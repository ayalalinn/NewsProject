from fastapi import APIRouter, HTTPException, Query
from app.schemas.article import Article, ArticleCreate
from app.services.db import get_article, save_article, list_articles
from app.realtime import notifier  # לשידור ה-SSE אחרי יצירה
import asyncio

router = APIRouter(prefix="/api", tags=["articles"])

@router.get("/article/{article_id}", response_model=Article)
def read_article(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/article", response_model=Article, status_code=201)
async def create_article(payload: ArticleCreate):
    article = save_article(payload)
    # נשלח אירוע SSE – עכשיו ב-async נוודא שזה נשלח
    await notifier.publish({"type": "news.notify", "news_id": article.id})
    return article

@router.get("/articles")
def list_articles_api(limit: int = Query(20, ge=1, le=50), cursor: str | None = None):
    items, next_cursor = list_articles(limit=limit, start_after=cursor)
    return {
        "items": [i.model_dump(mode="json") for i in items],
        "next_cursor": next_cursor
    }
