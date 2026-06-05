"""Cross-session project continuity."""

from __future__ import annotations

from typing import Any


def restore_context(*, project: dict[str, Any], timeline: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "project_id": project.get("id"),
        "summary": f"Resuming {project.get('name', 'project')} with {len(timeline)} events",
        "last_events": timeline[-5:],
    }
