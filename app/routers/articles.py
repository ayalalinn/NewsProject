
"""from fastapi import APIRouter, HTTPException
from app.schemas.article import Article
from app.services.db import get_article  # 👈 שימוש בשכבת השירותים

#מגדיר נתיב חדש שמוגדר לעבוד עם נתיבים שמתחילים באיפיאי הטאגס זה כדי לעזור לקשר נתיב לתוכן העמוד
router = APIRouter(prefix="/api", tags=["articles"])

#יוצר נתיב חדש ריספונס מודל=ארטיקל אומר להחזיר תגובה בדיוק במודל של ארטיקל
@router.get("/article/{article_id}", response_model=Article)
def read_article(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article"""
    
    # app/routers/articles.py
from fastapi import APIRouter, HTTPException
from app.schemas.article import Article, ArticleCreate
from app.services.db import get_article, save_article

router = APIRouter(prefix="/api", tags=["articles"])

@router.get("/article/{article_id}", response_model=Article)
def read_article(article_id: str):
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/article", response_model=Article, status_code=201)
def create_article(payload: ArticleCreate):
    """יוצר/שומר כתבה חדשה ומחזיר אותה (כולל id)."""
    article = save_article(payload)
    return article


from fastapi import Query
from app.services.db import list_articles

@router.get("/api/articles")
def list_articles_api(limit: int = Query(20, ge=1, le=50), cursor: str | None = None):
    """
    מחזיר רשימת כתבות ראשונה/הבא בתור עם פג'ינציה (cursor).
    GET /api/articles?limit=20&cursor=<last_id>
    """
    items, next_cursor = list_articles(limit=limit, start_after=cursor)
    return {
        "items": [i.model_dump(mode="json") for i in items],
        "next_cursor": next_cursor
    }


