
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


