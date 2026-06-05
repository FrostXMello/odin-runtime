"""Reranking pipeline for retrieval."""

from __future__ import annotations

from typing import Any


def rerank_results(query: str, items: list[dict], *, importance_weight: float = 0.3) -> list[dict[str, Any]]:
    def score(item: dict) -> float:
        base = item.get("score", item.get("importance", 0.5))
        return base + importance_weight * item.get("importance", 0.5)

    return sorted(items, key=score, reverse=True)
