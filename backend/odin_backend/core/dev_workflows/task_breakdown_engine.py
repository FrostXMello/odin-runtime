from __future__ import annotations

from typing import Any


def breakdown_goal(*, goal: str) -> list[dict[str, Any]]:
    return [{"title": f"Analyze {goal}", "order": 1}, {"title": f"Implement {goal}", "order": 2}, {"title": f"Validate {goal}", "order": 3}]
