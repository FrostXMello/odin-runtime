"""Assemble reasoning chains from agent steps."""

from __future__ import annotations

from typing import Any


def assemble_chain(steps: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "depth": len(steps),
        "agents": [s.get("agent_kind") for s in steps],
        "avg_confidence": sum(float(s.get("confidence", 0)) for s in steps) / max(1, len(steps)),
        "steps": steps,
    }
