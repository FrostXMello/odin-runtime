"""Message context assembly."""

from __future__ import annotations

from typing import Any


def build_context(*, projects: list[dict], tasks: list[dict]) -> dict[str, Any]:
    return {"project_count": len(projects), "open_tasks": len(tasks)}
