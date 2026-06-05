"""Proactive assistance triggers for copilot mode."""

from __future__ import annotations

from typing import Any


async def evaluate_proactive_triggers(app: Any, *, context: dict[str, Any]) -> list[dict[str, str]]:
    triggers: list[dict] = []
    temporal = context.get("temporal", {})
    if isinstance(temporal, dict) and temporal.get("event_count", 0) > 10:
        triggers.append({"trigger": "high_activity", "message": "Workspace activity is elevated"})
    desktop = context.get("desktop", {})
    if desktop.get("memory_pressure"):
        triggers.append({"trigger": "resource_pressure", "message": "Consider deferring heavy tasks"})
    return triggers
