"""Link memories to projects."""

from __future__ import annotations

from typing import Any


def link_to_project(*, project_id: str, memories: list[dict[str, Any]]) -> dict[str, Any]:
    linked = [{**m, "project_id": project_id} for m in memories]
    return {"project_id": project_id, "linked": len(linked), "memories": linked}
