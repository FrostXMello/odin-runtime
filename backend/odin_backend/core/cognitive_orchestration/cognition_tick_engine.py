from __future__ import annotations
from typing import Any


async def tick(app: Any) -> dict:
    results = {}
    if hasattr(app, "cognitive_kernel"):
        results["kernel"] = await app.cognitive_kernel.heartbeat()
    return results
