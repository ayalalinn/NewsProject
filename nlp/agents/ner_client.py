from __future__ import annotations
import httpx
from typing import List
from nlp.schemas import Entity
from nlp.settings import MCP_SERVER_URL

class NerClient:
    def __init__(self, base_url: str | None = None, timeout: float = 20.0, retries: int = 2):
        self.base_url = base_url or MCP_SERVER_URL
        self.timeout = timeout
        self.retries = retries

    def health(self) -> bool:
        try:
            import requests
            r = requests.get(f"{self.base_url}/docs", timeout=3)
            return r.status_code < 500
        except Exception:
            return False

    def _merge_adjacent(self, ents: List[Entity]) -> List[Entity]:
        if not ents: return []
        ents = sorted(ents, key=lambda e: (e.start or 0, e.end or 0))
        def prefer_type(a: str, b: str) -> str:
            order = {"PERSON": 3, "ORG": 2, "LOCATION": 1}
            a, b = (a or "").upper(), (b or "").upper()
            return b if order.get(b, 0) > order.get(a, 0) else a

        merged: List[Entity] = []
        cur = ents[0]
        for nxt in ents[1:]:
            gap = (nxt.start - cur.end) if (cur.end is not None and nxt.start is not None) else 999
            if gap <= 1:  # צמוד/חופף → מאחדים
                new_type = prefer_type(cur.type, nxt.type)
                sep = " " if (cur.end is not None and nxt.start is not None and nxt.start > cur.end) else ""
                new_text = f"{cur.text}{sep}{nxt.text}".strip()
                new_start = cur.start if cur.start is not None else nxt.start
                new_end = nxt.end if nxt.end is not None else cur.end
                cur = Entity(type=new_type or cur.type, text=new_text, start=new_start, end=new_end)
            else:
                merged.append(cur); cur = nxt
        merged.append(cur)
        return merged

    def extract(self, text: str) -> List[Entity]:
        last_err = None
        for _ in range(self.retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    r = client.post(f"{self.base_url}/tools/ner", json={"text": text})
                    r.raise_for_status()
                    data = r.json()
                    raw_ents = data.get("entities", []) or []
                    ents = [Entity(type=(e.get("type") or ""), text=(e.get("text") or ""),
                                   start=e.get("start"), end=e.get("end"))
                            for e in raw_ents if (e.get("text") or "").strip()]
                    return self._merge_adjacent(ents)
            except Exception as e:
                last_err = e
        raise RuntimeError(f"[NER] failed after retries: {last_err}")
