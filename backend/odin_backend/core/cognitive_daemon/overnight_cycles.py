from __future__ import annotations
from typing import Any


async def run(app: Any) -> dict:
    if hasattr(app, "cognitive_orchestration"):
        return await app.cognitive_orchestration.overnight_cycle()
    return {"cycle": "lightweight"}
