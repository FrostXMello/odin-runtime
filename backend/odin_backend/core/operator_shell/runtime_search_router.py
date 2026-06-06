"""Runtime search routing."""

from __future__ import annotations

from typing import Any


async def search_route(app: Any, query: str) -> dict[str, Any]:
    if hasattr(app, "vector_memory"):
        return await app.vector_memory.search_hybrid(query, limit=10)
    return {"accepted": False, "results": []}
