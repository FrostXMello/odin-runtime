from __future__ import annotations
from typing import Any


async def resume(app: Any) -> dict:
    if hasattr(app, "project_memory"):
        return await app.project_memory.resume()
    return {"restored": False}
