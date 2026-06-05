"""Strategic projection from world state."""

from __future__ import annotations

from typing import Any


def project_strategy(entities: list[dict], *, goal: str) -> dict[str, Any]:
    avg_conf = sum(e.get("confidence", 0.5) for e in entities) / max(len(entities), 1)
    return {
        "goal": goal,
        "entity_count": len(entities),
        "aggregate_confidence": round(avg_conf, 4),
        "projection": f"strategic_path_toward_{goal}",
        "assumptions": ["local_state_accurate", "no_hidden_execution"],
    }
