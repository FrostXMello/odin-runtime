from __future__ import annotations
from typing import Any


async def restore(app: Any) -> dict:
    if hasattr(app, "conversational_presence"):
        return await app.conversational_presence.connect()
    return {"restored": False}
