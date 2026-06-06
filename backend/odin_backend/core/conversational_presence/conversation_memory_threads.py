from __future__ import annotations
from typing import Any


async def recall_thread(app: Any, *, topic: str) -> dict[str, Any]:
    if hasattr(app, "memory_threads"):
        return await app.memory_threads.activate(topic=topic)
    return {"anchors": [topic[:80]]}
