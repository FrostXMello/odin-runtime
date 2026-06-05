"""Embedding cache."""

from __future__ import annotations

from typing import Any


class EmbeddingCache:
    def __init__(self, max_entries: int = 500) -> None:
        self._cache: dict[str, list[float]] = {}
        self._max = max_entries

    def get(self, key: str) -> list[float] | None:
        return self._cache.get(key)

    def put(self, key: str, vector: list[float]) -> None:
        if len(self._cache) >= self._max:
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = vector

    def size(self) -> int:
        return len(self._cache)
