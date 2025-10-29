# nlp/agents/enricher.py
from __future__ import annotations
import httpx
from typing import List, Dict, Any

class NerEnricher:
    """
    Agent פנימי: מקבל טקסט, קורא ל-MCP NER (ב-8001), ומחזיר ישויות נקיות.
    """
    def __init__(self, base_url: str = "http://127.0.0.1:8001"):
        self.base_url = base_url
        self._client = httpx.Client(timeout=20.0)

    def health(self) -> Dict[str, Any]:
        r = self._client.get(f"{self.base_url}/health")
        r.raise_for_status()
        return r.json()

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        payload = {"text": text}
        r = self._client.post(f"{self.base_url}/tools/ner", json=payload)
        r.raise_for_status()
        data = r.json()
        return data.get("entities", [])

if __name__ == "__main__":
    agent = NerEnricher()
    print("Health:", agent.health())
    ents = agent.extract_entities("Elon Musk met with the CEO of OpenAI in San Francisco to discuss AI.")
    for e in ents:
        print(e)
