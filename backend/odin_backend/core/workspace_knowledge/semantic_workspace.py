"""Semantic workspace index."""

from __future__ import annotations

from typing import Any


class SemanticWorkspace:
    def __init__(self) -> None:
        self._chunks: list[dict[str, Any]] = []

    def index(self, *, text: str, metadata: dict | None = None) -> dict[str, Any]:
        chunk = {"text": text[:500], "metadata": metadata or {}}
        self._chunks.append(chunk)
        return chunk

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        q = query.lower()
        hits = [c for c in self._chunks if q in c["text"].lower()]
        return hits[:limit]
