from __future__ import annotations
from typing import Any


async def plan(app: Any) -> dict:
    if hasattr(app, "daily_operator_experience"):
        return await app.daily_operator_experience.startup()
    return {"plan": "focus block"}
