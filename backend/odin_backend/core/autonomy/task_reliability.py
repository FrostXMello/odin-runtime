"""Autonomous task reliability (Prompt 38)."""

from __future__ import annotations

from typing import Any


def estimate_viability(*, complexity: float, resources_ok: bool, approvals: bool) -> dict[str, Any]:
    base = 0.7 if resources_ok else 0.35
    if not approvals:
        base *= 0.5
    prob = max(0.05, min(0.95, base - complexity * 0.2))
    return {"probability": round(prob, 3), "viable": prob > 0.45}


def analyze_execution_risk(*, action: str, destructive: bool = False) -> dict[str, Any]:
    risk = "high" if destructive else "medium" if "delete" in action.lower() else "low"
    return {"action": action, "risk": risk, "requires_approval": risk != "low"}


def select_retry_strategy(*, error: str, retries: int) -> dict[str, Any]:
    if retries >= 3:
        return {"strategy": "escalate", "delay_s": 0}
    if "timeout" in error.lower():
        return {"strategy": "backoff", "delay_s": 2 ** retries}
    return {"strategy": "immediate", "delay_s": 0}


def plan_rollback(*, steps: list[str]) -> dict[str, Any]:
    return {"steps": list(reversed(steps)), "safe": True}


def objective_stability(*, changes: int, window_hours: float) -> dict[str, Any]:
    stable = changes <= 2 or window_hours > 24
    return {"stable": stable, "changes": changes, "window_hours": window_hours}
