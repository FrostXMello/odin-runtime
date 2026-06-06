from __future__ import annotations
from typing import Any


async def recover(app: Any) -> dict:
    if hasattr(app, "daily_continuity"):
        return await app.daily_continuity.resume_summary()
    return {"workflows": []}
