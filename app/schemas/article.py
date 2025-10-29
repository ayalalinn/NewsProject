from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class Article(BaseModel):
    id: str
    title: str
    published_at: str
    content: str
    category: str               # Zero-shot category
    entities: List[str]         # NER tags
    image_url: HttpUrl
    source_url: HttpUrl
    external_id: Optional[str] = None

class ArticleCreate(BaseModel):
    id: Optional[str] = None    # אפשר לשלוח או שנייצר UUID
    title: str
    published_at: str
    content: str
    category: str
    entities: List[str]
    image_url: HttpUrl
    source_url: HttpUrl
    external_id: Optional[str] = None
