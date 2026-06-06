"""Archival retention policies."""

from __future__ import annotations

from typing import Any


def retention_policy(*, project_id: str, age_days: int) -> dict[str, Any]:
    archive = age_days > 90
    return {"project_id": project_id, "archive": archive, "retain_days": 90 if archive else age_days}


def apply_archival(*, cache_entries: int) -> dict[str, Any]:
    should_archive = cache_entries > 500
    return {
        "archive": should_archive,
        "threshold": 500,
        "cache_entries": cache_entries,
        "action": "compress_and_move_cold" if should_archive else "none",
    }
