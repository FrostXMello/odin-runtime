from __future__ import annotations
from typing import Any


async def tick(app: Any, *, idle_s: float = 0.0) -> dict:
    if hasattr(app, "cognitive_daemon_v2"):
        return await app.cognitive_daemon_v2.overnight()
    return {"tick": True, "idle_s": idle_s}
