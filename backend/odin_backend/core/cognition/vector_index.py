"""Lightweight vector index — token overlap similarity."""

from __future__ import annotations

from odin_backend.core.memory.context.embeddings import rank_by_similarity, similarity, tokenize


class VectorIndex:
    def __init__(self) -> None:
        self._entries: dict[str, str] = {}

    def upsert(self, key: str, text: str) -> None:
        self._entries[key] = text

    def remove(self, key: str) -> None:
        self._entries.pop(key, None)

    def search(self, query: str, *, limit: int = 10) -> list[tuple[str, float]]:
        return rank_by_similarity(query, self._entries.items(), limit=limit)

    @staticmethod
    def score(a: str, b: str) -> float:
        return similarity(a, b)

    @staticmethod
    def tokens(text: str) -> set[str]:
        return tokenize(text)
