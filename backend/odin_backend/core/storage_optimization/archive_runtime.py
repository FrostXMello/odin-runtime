"""Archive old data."""

from __future__ import annotations

from typing import Any


def archive_entries(entries: list[dict[str, Any]], *, keep: int = 100) -> dict[str, Any]:
    if len(entries) <= keep:
        return {"archived": 0, "remaining": len(entries)}
    archived = len(entries) - keep
    return {"archived": archived, "remaining": keep}
