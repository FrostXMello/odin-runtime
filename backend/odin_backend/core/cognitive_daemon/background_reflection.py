from __future__ import annotations
from typing import Any


async def reflect(app: Any) -> dict[str, Any]:
    if hasattr(app, "reflection"):
        snap = getattr(app.reflection, "snapshot", lambda: {})()
        return {"reflection": snap}
    return {"reflection": "deferred"}
