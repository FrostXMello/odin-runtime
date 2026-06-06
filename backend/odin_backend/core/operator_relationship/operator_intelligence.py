"""Operator-aware intelligence (Prompt 38)."""

from __future__ import annotations

from typing import Any


def build_operator_context(*, active_app: str, project: str | None, idle_minutes: float) -> dict[str, Any]:
    return {"active_app": active_app, "project": project, "idle_minutes": idle_minutes, "focus": idle_minutes < 5}


def predict_workflow(*, history: list[str]) -> dict[str, Any]:
    if not history:
        return {"next": "explore", "confidence": 0.3}
    last = history[-1]
    return {"next": last, "confidence": 0.6}


def infer_project_priority(*, projects: list[dict]) -> list[dict]:
    return sorted(projects, key=lambda p: p.get("last_active", 0), reverse=True)


def learn_habit(*, action: str, hour: int) -> dict[str, Any]:
    return {"action": action, "hour": hour, "pattern": f"often_{action}_at_{hour}"}


def predict_intent(*, signals: list[str]) -> dict[str, Any]:
    coding = sum(1 for s in signals if "code" in s or "debug" in s)
    return {"intent": "coding" if coding else "general", "confidence": min(1.0, 0.4 + coding * 0.15)}


def interruption_allowed(*, focus_session: bool, priority: str) -> bool:
    if focus_session and priority != "critical":
        return False
    return True
