import asyncio
from typing import AsyncIterator

#מחזיק רשימה של תורים תור לכל לקוח שמתחבר
class Notifier:
    def __init__(self) -> None:
        self._subs: list[asyncio.Queue] = []
#יוצר תור חדש ומחזיר אותו ללקוח
    def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self._subs.append(q)
        return q
#עובר על כל התורים ודוחף לשם את הנתון החדש
    async def publish(self, data: dict):
        for q in list(self._subs):
            await q.put(data)

notifier = Notifier()

async def sse_events(q: asyncio.Queue) -> AsyncIterator[bytes]:
    try:
        while True:
            data = await q.get()
            yield f"data: {data}\n\n".encode("utf-8")
    except asyncio.CancelledError:
        return
