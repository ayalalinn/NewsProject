from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from datetime import datetime


class NewsRaw(BaseModel):
    """מודל לידיעה גולמית שנכנסת מה־Webhook/WebSocket"""
    external_id: str = Field(..., description="מזהה ייחודי (hash(title+url))")
    title: str
    summary: Optional[str] = None
    url: HttpUrl
    source: Optional[str] = None
    lang: Optional[str] = None
    published_at: Optional[datetime] = None
    fetched_at: datetime


class Entity(BaseModel):
    """ישות שמזוהה ע\"י NER (אדם, מקום וכו׳)"""
    type: str  # PERSON | ORG | GPE | LOC | EVENT
    text: str
    start: Optional[int] = None
    end: Optional[int] = None


class NewsEnriched(BaseModel):
    """ידיעה לאחר עיבוד ע\"י הסוכנים (NER, תמונה, תקציר וכו׳)"""
    external_id: str
    categories: List[str]
    ner: List[Entity]
    image_urls: List[HttpUrl] = []
    summary: Optional[str] = None
    model_meta: Optional[dict] = None


class NotifyEvent(BaseModel):
    """אירוע שנשלח ל־Frontend בזמן אמת (SSE/WebSocket)"""
    news_id: str
    categories: List[str]


class DeadLetter(BaseModel):
    """הודעות שנכשלו בעיבוד"""
    external_id: Optional[str]
    raw_payload: dict
    reason: str
    timestamp: datetime
