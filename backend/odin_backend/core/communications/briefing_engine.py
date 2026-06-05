"""Daily briefing generation."""

from __future__ import annotations

from typing import Any


def generate_briefing(*, projects: list[dict], tasks: list[dict], events: list[dict]) -> dict[str, Any]:
    return {
        "summary": f"{len(projects)} active projects, {len(tasks)} open tasks",
        "highlights": [t.get("title", "") for t in tasks[:5]],
        "events": len(events),
    }
