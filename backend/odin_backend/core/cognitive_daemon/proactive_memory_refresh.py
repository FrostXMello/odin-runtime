from __future__ import annotations
from typing import Any


async def refresh(app: Any) -> dict[str, Any]:
    if hasattr(app, "memory_threads"):
        return await app.memory_threads.recall()
    return {"refreshed": False}
