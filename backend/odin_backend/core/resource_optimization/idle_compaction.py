"""Idle memory compaction."""

from __future__ import annotations

from typing import Any


def compact(*, cache_size: int, threshold: int = 100) -> dict[str, Any]:
    if cache_size > threshold:
        return {"compacted": True, "freed_entries": cache_size - threshold // 2}
    return {"compacted": False, "freed_entries": 0}
