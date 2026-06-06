from __future__ import annotations
from typing import Any


async def validate_light(app: Any) -> dict:
    if hasattr(app, "validation_fabric"):
        snap = getattr(app.validation_fabric, "snapshot", lambda: {})()
        return {"validation": snap, "lightweight": True}
    return {"skipped": True}
