from pydantic import BaseModel, HttpUrl
from typing import List


#מגדיר מודל שמוודא את סוג הנתונים כדי שידיעה חדשתית תתקבל במבנה מסוים ומוסכם
class Article(BaseModel):           
    id: str
    title: str
    published_at: str
    content: str
    category: str            # Zero-shot category (ימולא בהמשך ע"י שירות NLP)
    entities: List[str]      # NER tags (ימולא בהמשך ע"י שירות NLP)
    image_url: HttpUrl
    source_url: HttpUrl
from typing import Optional


class ArticleCreate(BaseModel):
    id: Optional[str] = None   # אפשר לשלוח או שנייצר לבד
    title: str
    published_at: str
    content: str
    category: str
    entities: List[str]
    image_url: HttpUrl
    source_url: HttpUrl
