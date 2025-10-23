# app/services/db.py
from typing import Optional
from uuid import uuid4
import os

import firebase_admin
from firebase_admin import credentials, firestore
from pydantic import ValidationError

from app.schemas.article import Article, ArticleCreate
from app.core.config import FIRESTORE_COLLECTION, GOOGLE_APPLICATION_CREDENTIALS

_initialized = False
_db = None

def _ensure_init():
    """
    מאתחל Firebase פעם אחת. אם כבר מאותחל (בגלל reload), עושה reuse במקום initialize נוסף.
    """
    global _initialized, _db
    if _initialized and _db is not None:
        return

    cred_path = GOOGLE_APPLICATION_CREDENTIALS
    if not cred_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS is not set (check your .env)")

    # תומך גם בנתיב יחסי (./secrets/...) וגם במלא
    if not os.path.exists(cred_path):
        alt = os.path.abspath(cred_path)
        if not os.path.exists(alt):
            raise FileNotFoundError(f"Firebase service account file not found: {cred_path}")
        cred_path = alt

    try:
        # אם כבר יש אפליקציה מאותחלת (עקב --reload), נשתמש בה
        app = firebase_admin.get_app()
    except ValueError:
        # אין אפליקציה — נאתחל חדשה
        cred = credentials.Certificate(cred_path)
        app = firebase_admin.initialize_app(cred)

    # קבלת לקוח Firestore מתוך האפליקציה
    _db = firestore.client(app)
    _initialized = True


def get_article(article_id: str) -> Optional[Article]:
    _ensure_init()
    doc_ref = _db.collection(FIRESTORE_COLLECTION).document(article_id)
    snap = doc_ref.get()
    if not snap.exists:
        return None
    data = snap.to_dict() or {}
    data["id"] = article_id
    try:
        return Article(**data)
    except ValidationError:
        return None


def save_article(payload: ArticleCreate) -> Article:
    _ensure_init()
    aid = payload.id or str(uuid4())
    art = Article(id=aid, **payload.model_dump(exclude={"id"}))
    doc_ref = _db.collection(FIRESTORE_COLLECTION).document(aid)
    
    to_store = art.model_dump(mode="json", exclude={"id"})
#            ^^^^^^^^^^^^^  חשוב! מבקש ממודל להחזיר טיפוסים JSON (מחרוזות במקום HttpUrl)

    doc_ref.set(to_store)
    return art
