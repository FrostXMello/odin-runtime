from __future__ import annotations
from typing import Any

STAGES = (
    "observe",
    "analyze",
    "propose",
    "simulate",
    "validate",
    "request_approval",
    "apply_branch",
    "benchmark",
    "rollback_check",
    "learn",
)

def next_stage(current: str | None) -> str:
    if not current:
        return STAGES[0]
    idx = STAGES.index(current) if current in STAGES else -1
    return STAGES[min(idx + 1, len(STAGES) - 1)]

def cycle_budget(*, depth: int, max_depth: int = 3) -> dict[str, Any]:
    return {"depth": depth, "max_depth": max_depth, "allowed": depth < max_depth}
