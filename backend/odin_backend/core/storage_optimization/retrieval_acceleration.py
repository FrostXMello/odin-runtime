"""Retrieval acceleration via cache."""

from __future__ import annotations

from typing import Any


def accelerate(query: str, cache_hits: int, total: int) -> dict[str, Any]:
    hit_rate = cache_hits / max(total, 1)
    return {"query": query, "hit_rate": hit_rate, "optimized": hit_rate > 0.3}
