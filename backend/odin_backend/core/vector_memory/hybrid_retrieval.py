"""Hybrid keyword + embedding retrieval."""

from __future__ import annotations

from typing import Any


def hybrid_retrieve(*, keyword_hits: list[dict], semantic_hits: list[dict], limit: int = 10) -> list[dict[str, Any]]:
    merged: dict[str, dict] = {}
    for hit in keyword_hits:
        key = hit.get("id", hit.get("text", ""))[:80]
        merged[key] = {**hit, "score": hit.get("score", 0.4) * 0.4}
    for hit in semantic_hits:
        key = hit.get("id", hit.get("text", ""))[:80]
        base = merged.get(key, {**hit, "score": 0.0})
        base["score"] = round(base.get("score", 0) + hit.get("score", 0.5) * 0.6, 4)
        merged[key] = base
    ranked = sorted(merged.values(), key=lambda x: x.get("score", 0), reverse=True)
    return ranked[:limit]
