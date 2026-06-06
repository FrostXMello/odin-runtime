from __future__ import annotations
from typing import Any


async def beat(app: Any) -> dict:
    if hasattr(app, "cognitive_kernel"):
        return await app.cognitive_kernel.heartbeat()
    return {"beat": True}
