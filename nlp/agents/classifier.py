# nlp/agents/classifier.py
from typing import List
from transformers import pipeline

# ברירות מחדל יציבות לסיווג
DEFAULT_LABELS: List[str] = ["Politics", "Finance", "Science", "Culture", "Sport", "Tech"]
MODEL_NAME = "facebook/bart-large-mnli"

# טוענים פעם אחת (ריצה על CPU)
_zero_shot = pipeline("zero-shot-classification", model=MODEL_NAME)

def classify(text: str, labels: List[str] | None = None) -> List[str]:
    if not text:
        return []
    labels = labels or DEFAULT_LABELS
    res = _zero_shot(text, candidate_labels=labels, multi_label=True)
    pairs = list(zip(res["labels"], res["scores"]))
    selected = [lbl for lbl, score in pairs if score >= 0.4]
    if not selected and res["labels"]:
        selected = [res["labels"][0]]
    return selected