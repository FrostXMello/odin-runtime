"""Emergency memory reclaim."""

from __future__ import annotations

from typing import Any


async def emergency_reclaim(app: Any) -> dict[str, Any]:
    reclaimed: list[str] = []
    if hasattr(app, "local_ai"):
        for model in list(getattr(app.local_ai, "_loaded", set())):
            await app.local_ai.evict(model)
            reclaimed.append(f"model:{model}")
    if hasattr(app, "vector_memory") and hasattr(app.vector_memory, "compact"):
        compact = await app.vector_memory.compact()
        if compact.get("evicted"):
            reclaimed.append("vector_cache")
    return {"reclaimed": reclaimed, "count": len(reclaimed)}
