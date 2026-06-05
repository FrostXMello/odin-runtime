"""Rerank retrieval results."""

from __future__ import annotations

from typing import Any


def rerank(query: str, items: list[dict[str, Any]], scores: list[float]) -> list[dict[str, Any]]:
    if len(scores) != len(items):
        return items
    enriched = [{**it, "rerank_score": sc} for it, sc in zip(items, scores)]
    enriched.sort(key=lambda x: -x["rerank_score"])
    return enriched
