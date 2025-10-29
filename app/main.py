#מייבא את המחלקה
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#מייבא את הנתיב שיצרנו בארטיקל כדי לחבר איפיאי לשרת הראשי

from app.routers.articles import router as articles_router
import gradio as gr
#שילוב ממשק המתמש בשרת
from app.ui import build_ui
#יוצר את אובייקט השרת
app = FastAPI(title="NewsProject - Article View (MVC)")

# CORS פתוח לפיתוח (בפרודקשן מגבילים לדומיינים הרלוונטיים)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API
app.include_router(articles_router)

#יוצר נתיב בדיקה פשוט כדי לבדוק אם השרת רץ כמו שצריך
@app.get("/api/health")
def health():
    return {"status": "ok"}

# Mount Gradio UI תחת /article (תת-מערכת התצוגה)
gradio_app = build_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/article")


from fastapi import Request
from fastapi.responses import StreamingResponse
from app.realtime import notifier, sse_events

@app.get("/stream")
def stream(request: Request):
    q = notifier.subscribe()
    return StreamingResponse(sse_events(q), media_type="text/event-stream")
#נתיב לדף HTML
from fastapi.responses import HTMLResponse

from fastapi.responses import HTMLResponse

from pathlib import Path
from fastapi.responses import HTMLResponse

LIVE_HTML = Path(__file__).resolve().parent / "templates" / "live.html"

@app.get("/live", response_class=HTMLResponse)
def live_page():
    return LIVE_HTML.read_text(encoding="utf-8")


