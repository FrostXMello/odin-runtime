"""Cross-node workload balancing."""

from __future__ import annotations

from typing import Any


def balance(loads: dict[str, float]) -> dict[str, Any]:
    if not loads:
        return {"balanced": True, "assignments": {}}
    avg = sum(loads.values()) / len(loads)
    assignments = {k: round(avg, 4) for k in loads}
    return {"balanced": True, "assignments": assignments, "average_load": round(avg, 4)}
