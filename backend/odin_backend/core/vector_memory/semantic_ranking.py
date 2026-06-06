"""Semantic reranking for retrieval results."""

from __future__ import annotations

from typing import Any


def rerank(*, query: str, hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    q = query.lower()
    for hit in hits:
        text = str(hit.get("text", "")).lower()
        overlap = sum(1 for w in q.split() if w in text)
        hit["rank_score"] = round(hit.get("score", 0.5) + overlap * 0.05, 4)
    return sorted(hits, key=lambda h: h.get("rank_score", 0), reverse=True)
