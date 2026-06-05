"""In-memory semantic index over embeddings."""

from __future__ import annotations

import math
from typing import Any


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class SemanticIndex:
    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def add(self, entry: dict[str, Any]) -> None:
        self._entries.append(entry)

    def search(self, query_vec: list[float], *, limit: int = 10) -> list[dict[str, Any]]:
        scored = []
        for e in self._entries:
            score = cosine(query_vec, e.get("embedding", []))
            scored.append({**e, "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored[:limit]

    def clear(self) -> None:
        self._entries.clear()
