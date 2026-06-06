from __future__ import annotations
from typing import Any


async def recall(app: Any, *, query: str) -> dict:
    if hasattr(app, "memory_fabric_v2"):
        return await app.memory_fabric_v2.rehydrate_context(session=query)
    return {"query": query, "recalled": True}
