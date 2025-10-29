# nlp/agents/image_fetcher.py
from __future__ import annotations
from typing import List, Dict, Optional
import os
import urllib.parse
import httpx

# Cloudinary (אופציונלי – רק אם יש קרדנטיאלס בסביבה)
try:
    import cloudinary
    import cloudinary.uploader
    _HAS_CLOUDINARY = True
except Exception:
    _HAS_CLOUDINARY = False

CLOUD_NAME   = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUD_KEY    = os.getenv("CLOUDINARY_API_KEY", "")
CLOUD_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

if _HAS_CLOUDINARY and CLOUD_NAME and CLOUD_KEY and CLOUD_SECRET:
    cloudinary.config(
        cloud_name=CLOUD_NAME,
        api_key=CLOUD_KEY,
        api_secret=CLOUD_SECRET,
        secure=True,
    )
else:
    _HAS_CLOUDINARY = False  # ודא שלא ננסה להשתמש אם חסר משהו

WIKI_SUMMARY_API = "https://en.wikipedia.org/api/rest_v1/page/summary/"
# יש גם thumb מהתוצאה; אם לא קיים, אפשר לנסות endpoint אחר, אבל נספיק ל-MVP.

def _norm_entities(entities: List[Dict | object]) -> List[Dict]:
    norm: List[Dict] = []
    for e in entities:
        if hasattr(e, "model_dump"):
            norm.append(e.model_dump())
        elif isinstance(e, dict):
            norm.append(e)
        else:
            norm.append({
                "type": getattr(e, "type", "") or "",
                "text": getattr(e, "text", "") or "",
                "start": getattr(e, "start", None),
                "end": getattr(e, "end", None),
            })
    return norm

def _candidate_texts(entities: List[Dict]) -> List[str]:
    """
    מחזיר מועמדים לשאילתא לפי עדיפויות: PERSON > ORG > LOCATION, בלי כפילויות, בלי ריקים.
    """
    prio = {"PERSON": 0, "ORG": 1, "LOCATION": 2}
    cleaned = []
    for e in entities:
        t = (e.get("type") or "").upper()
        txt = (e.get("text") or "").strip()
        if not txt:
            continue
        cleaned.append((prio.get(t, 99), txt))
    cleaned.sort(key=lambda x: x[0])
    seen = set()
    out: List[str] = []
    for _, txt in cleaned:
        key = txt.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(txt)
    return out

async def _wiki_first_image(query: str) -> Optional[str]:
    """
    מחפש תמונה ראשונה מסיכום ויקיפדיה (REST summary).
    מחזיר URL של תמונה או None.
    """
    q = urllib.parse.quote(query)
    url = WIKI_SUMMARY_API + q
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.get(url)
            if r.status_code != 200:
                return None
            data = r.json()
            # סדר עדיפויות: thumbnail.source -> originalimage.source -> None
            thumb = (data.get("thumbnail") or {}).get("source")
            if thumb:
                return thumb
            orig = (data.get("originalimage") or {}).get("source")
            if orig:
                return orig
            return None
    except Exception:
        return None

def _cloudinary_placeholder(text: str) -> Optional[str]:
    """
    יוצר פלייסהולדר עם כותרת הידיעה. דורש קרדנטיאלס ב-ENV.
    """
    if not _HAS_CLOUDINARY:
        return None
    try:
        # משתמשים בתמונה דמו ומוסיפים overlay של הטקסט
        res = cloudinary.uploader.upload(
            "https://res.cloudinary.com/demo/image/upload/sample.jpg",
            transformation=[
                {
                    "overlay": {
                        "font_family": "Arial",
                        "font_size": 48,
                        "text": (text or "NEWS")[:80],
                    },
                    "gravity": "center",
                    "color": "white",
                }
            ],
            folder="news_placeholders",
        )
        return res.get("secure_url")
    except Exception:
        return None

async def images_for_entities(entities: List[Dict | object], headline: str = "") -> List[str]:
    """
    מנסה להביא עד 3 תמונות:
    1) חיפוש בויקיפדיה לפי ישויות (בעדיפות PERSON/ORG/LOCATION).
    2) אם לא נמצא כלום – נסה Cloudinary placeholder (אם זמינות הרשאות).
    """
    ents = _norm_entities(entities)
    candidates = _candidate_texts(ents)

    urls: List[str] = []
    for name in candidates:
        img = await _wiki_first_image(name)
        if img and img not in urls:
            urls.append(img)
        if len(urls) >= 3:
            break

    if not urls:
        ph = _cloudinary_placeholder(headline or "NEWS")
        if ph:
            urls.append(ph)

    return urls[:3]
