from __future__ import annotations
from typing import Any


async def plan(app: Any) -> dict[str, Any]:
    if hasattr(app, "daily_workflow"):
        return await app.daily_workflow.startup_routine()
    return {"plan": "focus engineering block"}
