# app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers.articles import router as articles_router
import gradio as gr
from app.ui import build_ui

# === Agents / Schemas (NER) ===
from nlp.agents.enricher import NerEnricher
from nlp.schemas import NewsRaw, NewsEnriched, Entity

app = FastAPI(title="NewsProject - Article View (MVC)")

# CORS פתוח לפיתוח (בפרודקשן מומלץ להגביל לדומיינים רלוונטיים)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API קיים
app.include_router(articles_router)

@app.get("/api/health")
def health():
    return {"status": "ok"}

# ====== NER Agent ======
# נשתמש בשרת ה-MCP NER המקומי שרץ על 8001
enricher = NerEnricher(base_url="http://127.0.0.1:8001")

@app.post("/api/enrich", response_model=NewsEnriched)
def api_enrich(payload: NewsRaw) -> NewsEnriched:
    """
    מקבל NewsRaw(text), קורא לשרת ה-NER (MCP) ומחזיר NewsEnriched
    עם entities + מידע מטה-דאטה בסיסי על המודל.
    """
    try:
        entities_raw = enricher.extract_entities(payload.text or "")
        entities = [
            Entity(
                type=e.get("type") or "MISC",
                text=e.get("text") or "",
                start=e.get("start"),
                end=e.get("end"),
                score=e.get("score"),
            )
            for e in entities_raw
        ]

        return NewsEnriched(
            raw=payload,
            entities=entities,
            model_meta={
                "ner_model": "dslim/bert-base-NER",
                "source": "mcp_server:8001",
            },
        )
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

# ====== Gradio UI תחת /article ======
gradio_app = build_ui()
app = gr.mount_gradio_app(app, gradio_app, path="/article")

