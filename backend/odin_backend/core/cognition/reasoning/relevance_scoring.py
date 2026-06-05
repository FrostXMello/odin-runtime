"""Relevance scoring for memory retrieval."""

from __future__ import annotations

from typing import Any


def score_relevance(query: str, item: dict[str, Any]) -> float:
    label = str(item.get("label", ""))
    conf = float(item.get("confidence", 0.5))
    sim = float(item.get("score", 0.0))
    q_tokens = set(query.lower().split())
    l_tokens = set(label.lower().split())
    overlap = len(q_tokens & l_tokens) / max(1, len(q_tokens))
    return min(0.99, overlap * 0.4 + sim * 0.4 + conf * 0.2)


def rank_items(query: str, items: list[dict[str, Any]], *, limit: int = 5) -> list[dict[str, Any]]:
    scored = [{**it, "relevance": score_relevance(query, it)} for it in items]
    scored.sort(key=lambda x: -x["relevance"])
    return scored[:limit]
