# nlp/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class NewsRaw(BaseModel):
    external_id: str
    title: str
    summary: Optional[str] = None
    url: str
    source: Optional[str] = None
    lang: Optional[str] = None
    published_at: Optional[str] = None  # ISO8601 string

class Entity(BaseModel):
    type: str                      # PERSON / ORG / GPE / LOC / EVENT ...
    text: str
    start: Optional[int] = None
    end: Optional[int] = None

class NewsEnriched(BaseModel):
    external_id: str
    categories: List[str] = Field(default_factory=list)
    ner: List[Entity] = Field(default_factory=list)
    image_urls: List[str] = Field(default_factory=list)
    summary: Optional[str] = None
    models_meta: dict = Field(default_factory=dict)  # <-- שינוי שם השדה

