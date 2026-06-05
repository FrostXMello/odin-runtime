"""Task ownership negotiation."""

from __future__ import annotations

from typing import Any


def negotiate(agents: list[dict], task: str) -> dict[str, Any]:
    if not agents:
        return {"owner": None}
    best = max(agents, key=lambda a: a.get("confidence", 0.5))
    return {"owner": best.get("agent_id"), "task": task, "confidence": best.get("confidence", 0.5)}
