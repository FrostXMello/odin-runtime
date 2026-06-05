"""Mission value scoring."""

from __future__ import annotations

from typing import Any


def value_mission(*, priority: str, complexity: float) -> dict[str, Any]:
    base = {"low": 0.3, "medium": 0.6, "high": 0.9}.get(priority, 0.5)
    return {"value_score": round(base * (1 + complexity * 0.2), 4), "priority": priority}
