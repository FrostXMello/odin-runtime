"""Operator synchronization scoring."""
from __future__ import annotations
from typing import Any

def sync_score(*, operator_actions: int, odin_responses: int) -> dict[str, Any]:
    ratio = odin_responses / max(operator_actions, 1)
    return {"score": round(min(1.0, ratio), 3), "balanced": 0.4 <= ratio <= 1.2}
