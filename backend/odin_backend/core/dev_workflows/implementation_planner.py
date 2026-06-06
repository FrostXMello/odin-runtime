from __future__ import annotations

from typing import Any


def plan_implementation(*, tasks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"sequence": sorted(tasks, key=lambda t: t.get("order", 0)), "estimated_steps": len(tasks)}
