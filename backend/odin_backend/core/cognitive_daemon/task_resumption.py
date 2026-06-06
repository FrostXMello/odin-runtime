from __future__ import annotations
from typing import Any


async def resurface(app: Any) -> dict[str, Any]:
    if hasattr(app, "daily_continuity"):
        return await app.daily_continuity.resume_summary()
    return {"tasks": []}
