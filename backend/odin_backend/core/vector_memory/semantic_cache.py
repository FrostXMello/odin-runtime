"""Semantic deduplication cache."""

from __future__ import annotations

import hashlib
from typing import Any


class SemanticCache:
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    def key(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()[:16]

    def get(self, text: str) -> dict[str, Any] | None:
        return self._cache.get(self.key(text))

    def put(self, text: str, entry: dict[str, Any]) -> None:
        self._cache[self.key(text)] = entry

    def size(self) -> int:
        return len(self._cache)
