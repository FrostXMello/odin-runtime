from __future__ import annotations
from typing import Any


async def handle_interrupt(app: Any, *, reason: str = "operator") -> dict[str, Any]:
    if hasattr(app, "realtime_voice"):
        hit = app.realtime_voice.interrupt()
        return hit if isinstance(hit, dict) else {"interrupted": True, "reason": reason}
    return {"interrupted": True, "reason": reason}
