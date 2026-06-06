"""Storage analytics."""

from __future__ import annotations

from typing import Any


def analyze_storage(*, cache_size: int, cold_size: int, projects: int) -> dict[str, Any]:
    return {
        "cache_entries": cache_size,
        "cold_entries": cold_size,
        "projects": projects,
        "recommend_archive": cache_size > 500,
    }
