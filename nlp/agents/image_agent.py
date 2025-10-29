# nlp/agents/image_agent.py
from typing import List, Dict
import asyncio

# משתמש בפונקציה שכבר בנינו שמביאה תמונות מוויקיפדיה / פלייסהולדר מ-Cloudinary
from nlp.agents.image_fetcher import images_for_entities


class ImageAgent:
    """
    מקבל entities (מ-NER) + כותרת הידיעה (headline)
    ומחזיר עד 3 כתובות של תמונות רלוונטיות.
    """

    def __init__(self, max_images: int = 3):
        self.max_images = max_images

    async def enrich(self, entities: List[Dict], headline: str = "") -> List[str]:
        # המרה ל-dict אם הגיעו אובייקטי Pydantic/Entity
        norm = []
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

        # קורא לפונקציית העזר הא-סינכרונית שלנו
        urls = await images_for_entities(norm, headline=headline)
        # מקצר לפי מגבלה
        return urls[: self.max_images]


# דמו מהיר להרצה ידנית:
if __name__ == "__main__":
    async def _demo():
        ents = [
            {"type": "PERSON", "text": "Elon Musk"},
            {"type": "PERSON", "text": "Tim Cook"},
            {"type": "ORG", "text": "Apple"},
            {"type": "LOCATION", "text": "California"},
        ]
        agent = ImageAgent(max_images=3)
        imgs = await agent.enrich(ents, headline="Apple meeting")
        print("IMAGES:", imgs)

    asyncio.run(_demo())
