# nlp/agents/demo_ner_client.py
import httpx

BASE = "http://127.0.0.1:8001"

def main():
    # 1) בדיקת בריאות
    r = httpx.get(f"{BASE}/health", timeout=10)
    print("Health:", r.json())

    # 2) קריאת NER
    payload = {"text": "Elon Musk met with the CEO of OpenAI in San Francisco to discuss AI."}
    r = httpx.post(f"{BASE}/tools/ner", json=payload, timeout=20)
    r.raise_for_status()
    data = r.json()
    for ent in data.get("entities", []):
        print(ent)

if __name__ == "__main__":
    main()
