"""Simple in-memory fetch cache."""

from __future__ import annotations

from typing import Any


class FetchCache:
    def __init__(self, *, max_entries: int = 100) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._max = max_entries

    def get(self, url: str) -> dict[str, Any] | None:
        return self._cache.get(url)

    def set(self, url: str, value: dict[str, Any]) -> None:
        if len(self._cache) >= self._max:
            self._cache.pop(next(iter(self._cache)))
        self._cache[url] = value
