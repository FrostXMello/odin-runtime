from __future__ import annotations
from typing import Any


async def rehydrate(app: Any) -> dict:
    out = {}
    if hasattr(app, "persistent_cognition"):
        out["cognition"] = await app.persistent_cognition.rehydrate_session()
    if hasattr(app, "project_memory"):
        out["project"] = await app.project_memory.resume()
    return out
