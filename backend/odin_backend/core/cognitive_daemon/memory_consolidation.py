from __future__ import annotations
from typing import Any


async def consolidate(app: Any) -> dict:
    if hasattr(app, "memory_fabric"):
        return await app.memory_fabric.recall()
    return {"consolidated": False}
