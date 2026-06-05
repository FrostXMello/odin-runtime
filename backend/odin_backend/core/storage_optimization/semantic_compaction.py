"""Semantic compaction."""

from __future__ import annotations

from typing import Any


def compact_chunks(chunks: list[dict[str, Any]], *, target: int = 50) -> dict[str, Any]:
    if len(chunks) <= target:
        return {"compacted": 0, "chunks": chunks}
    ranked = sorted(chunks, key=lambda c: c.get("importance", 0.5), reverse=True)
    kept = ranked[:target]
    return {"compacted": len(chunks) - len(kept), "chunks": kept}
