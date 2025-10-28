# nlp/mcp_server/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import os, re

app = FastAPI(title="MCP - NER Tool")

# קביעת המודל (אנגלית)
NER_MODEL = os.getenv("NER_MODEL", "dslim/bert-base-NER")

# טוענים את המודל פעם אחת בלבד, עם איגוד בסיסי של תתי-מילים
_ner = pipeline(task="token-classification", model=NER_MODEL, aggregation_strategy="simple")


class NERRequest(BaseModel):
    text: str


@app.get("/health")
def health():
    return {"status": "ok", "model": NER_MODEL}


def _clean_word(word: str) -> str:
    if not word:
        return ""
    # "El ##on" -> "Elon"
    word = re.sub(r"\s*##", "", word)
    word = re.sub(r"\s{2,}", " ", word).strip()
    return word


def _to_py(e):
    """המרה לטיפוסים פייתוניים פשוטים לסריאליזציה תקינה + ניקוי תתי-טוקנים."""
    raw_word = str(e.get("word")) if e.get("word") is not None else ""
    word = _clean_word(raw_word)
    return {
        "type": str(e.get("entity_group")) if e.get("entity_group") is not None else None,
        "text": word,
        "start": int(e.get("start")) if e.get("start") is not None else None,
        "end": int(e.get("end")) if e.get("end") is not None else None,
        "score": float(e.get("score")) if e.get("score") is not None else None,
    }


def _merge_adjacent(entities):
    """
    מאחד ישויות רצופות מאותו type.
    אם הישות הבאה מתחילה בדיוק במקום שהקודמת נגמרת (צמוד), נדביק ללא רווח.
    אם יש פער (לרוב רווח בטקסט), נוסיף רווח חכם.
    """
    merged = []
    for e in entities:
        if (
            merged
            and merged[-1]["type"] == e["type"]
            and merged[-1]["end"] is not None
            and e["start"] is not None
            and (e["start"] == merged[-1]["end"] or e["start"] == merged[-1]["end"] + 1)
        ):
            prev_txt = merged[-1]["text"] or ""
            cur_txt = _clean_word(e.get("text", ""))

            # צמוד לחלוטין? אין רווח.
            if e["start"] == merged[-1]["end"]:
                sep = ""
            else:
                # יש פער (בד"כ רווח אמיתי) -> הוסף רווח רק אם אות-לאות
                sep = " " if (prev_txt and cur_txt and prev_txt[-1].isalnum() and cur_txt[0].isalnum()) else ""

            merged[-1]["text"] = _clean_word(f"{prev_txt}{sep}{cur_txt}")
            merged[-1]["end"] = e["end"]
            if merged[-1]["score"] is not None and e["score"] is not None:
                merged[-1]["score"] = (merged[-1]["score"] + e["score"]) / 2.0
        else:
            e["text"] = _clean_word(e.get("text", ""))
            merged.append(e)
    return merged


def _map_types(entities):
    """מפה קודים לקלים להבנה (אופציונלי)."""
    mapping = {"PER": "PERSON", "ORG": "ORG", "LOC": "LOCATION", "MISC": "MISC"}
    for e in entities:
        if e.get("type") in mapping:
            e["type"] = mapping[e["type"]]
    return entities


@app.post("/tools/ner")
def extract_ner(req: NERRequest):
    try:
        text = req.text or ""
        raw = _ner(text)
        safe = [_to_py(e) for e in raw]
        safe = _merge_adjacent(safe)
        safe = _map_types(safe)
        return {"model": NER_MODEL, "entities": safe}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
