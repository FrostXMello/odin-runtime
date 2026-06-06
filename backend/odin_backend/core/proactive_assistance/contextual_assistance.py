from __future__ import annotations
from typing import Any


async def contextualize(app: Any, *, context: str) -> dict:
    if hasattr(app, "daily_continuity"):
        return await app.daily_continuity.resume_summary()
    return {"context": context[:80]}
