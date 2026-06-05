"""Daemon memory compaction."""

from __future__ import annotations

from typing import Any


def compact_daemon_state(*, cache_entries: int, max_entries: int = 200) -> dict[str, Any]:
    evicted = max(0, cache_entries - max_entries)
    return {"evicted": evicted, "remaining": min(cache_entries, max_entries)}
