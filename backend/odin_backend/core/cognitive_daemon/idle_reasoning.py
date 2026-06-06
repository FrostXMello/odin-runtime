from __future__ import annotations
from typing import Any


async def idle_tick(app: Any) -> dict[str, Any]:
    if hasattr(app, "reasoning_streams"):
        return await app.reasoning_streams.push(thought="idle reflection")
    return {"idle": True}
