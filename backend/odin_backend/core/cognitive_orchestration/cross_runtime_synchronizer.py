from __future__ import annotations
from typing import Any


async def sync(app: Any) -> dict:
    synced = []
    for name in ("cognitive_workspace", "memory_fabric", "cognitive_daemon"):
        if hasattr(app, name):
            synced.append(name)
    return {"synced": synced}
