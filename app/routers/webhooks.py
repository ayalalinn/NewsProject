# app/routers/webhooks.py
from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import PlainTextResponse
from datetime import datetime
from app.services.kafka import send_to_kafka
from app.schemas.kafka_schemas import NewsRaw
import hashlib, hmac, os, json

# ניצור Router ייעודי לכל נושא ה־webhooks
router = APIRouter()

# סוד חתימה (לא חובה, אבל מומלץ להגנה על ה־Webhook)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# ----------------------------------------------------
# 🟢 שלב אימות — כאשר מקור חדשות רוצה לבדוק שה־Webhook קיים
# ----------------------------------------------------
@router.get("/websub")
async def websub_verify(
    hub_mode: str = None,
    hub_challenge: str = None,
    hub_topic: str = None
):
    """
    שרתים ששולחים ידיעות (כמו RSSHub, NewsAPI WebSub וכו׳)
    קודם שולחים בקשת אימות (GET). אנחנו פשוט מחזירים להם את ה־hub_challenge.
    """
    if hub_mode and hub_challenge:
        return PlainTextResponse(content=hub_challenge, status_code=200)
    raise HTTPException(status_code=400, detail="Missing hub params")


# ----------------------------------------------------
# 🟠 שלב קבלת ידיעות (POST)
# ----------------------------------------------------
@router.post("/websub")
async def websub_notify(request: Request, x_hub_signature: str | None = Header(None)):
    """
    זה הנתיב שאליו יגיעו ידיעות חדשות בזמן אמת.
    אם מגיעה חתימה (X-Hub-Signature), נבדוק שהיא תואמת את ה־secret.
    לאחר מכן נשלח את ההודעה ל־Kafka topic בשם news.raw.
    """

    raw_body = await request.body()

    # 🛡️ אימות חתימה (אם מוגדר WEBHOOK_SECRET)
    if WEBHOOK_SECRET and x_hub_signature:
        try:
            algo, sig = x_hub_signature.split("=", 1)
            mac = hmac.new(WEBHOOK_SECRET.encode(), raw_body, getattr(hashlib, algo))
            if not hmac.compare_digest(mac.hexdigest(), sig):
                raise HTTPException(status_code=401, detail="Invalid signature")
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid signature format")

    # נזהה את סוג התוכן (JSON / XML)
    content_type = request.headers.get("content-type", "")
    payload = None

    # 🧩 אם זה XML (כמו RSS/Atom feed)
    if "xml" in content_type or raw_body.strip().startswith(b"<"):
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(raw_body)
            item = root.find(".//{http://www.w3.org/2005/Atom}entry") or root.find(".//item")
            if item is None:
                return {"status": "ignored"}
            title = item.findtext(".//title") or item.findtext("title")
            link = item.findtext(".//link") or item.findtext("link")
            summary = item.findtext(".//summary") or item.findtext("description")
            payload = {
                "id": link or str(hash(title)),
                "title": title,
                "url": link,
                "summary": summary,
            }
        except Exception:
            return {"status": "parse_error"}

    # 🧩 אחרת — נניח שזה JSON רגיל
    else:
        payload = await request.json()

    # נבנה את אובייקט ה־NewsRaw לפי הסכמה שלך
    try:
        news = NewsRaw(
            external_id=payload.get("id") or payload.get("url") or str(hash(payload.get("title", ""))),
            title=payload.get("title", ""),
            summary=payload.get("summary"),
            url=payload.get("url"),
            source=payload.get("source", "external"),
            lang=payload.get("lang", "en"),
            published_at=payload.get("published_at"),
            fetched_at=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")

    # נשלח את הידיעה ל־Kafka
    await send_to_kafka(topic="news.raw", message=news.dict(), key=news.external_id)

    print(f"✅ כתבה נשלחה ל־Kafka: {news.title}")
    return {"status": "ok"}
