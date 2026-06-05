"""In-memory KV cache stub for repeated local inference."""

from __future__ import annotations

from typing import Any


class KVCache:
    def __init__(self, *, max_entries: int = 64) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._max_entries = max_entries

    def get(self, key: str) -> dict[str, Any] | None:
        return self._cache.get(key)

    def set(self, key: str, value: dict[str, Any]) -> None:
        if len(self._cache) >= self._max_entries:
            oldest = next(iter(self._cache))
            del self._cache[oldest]
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()
