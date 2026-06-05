"""Generate contextual copilot suggestions."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


async def generate_suggestions(app: Any, *, context: dict[str, Any]) -> list[dict[str, Any]]:
    suggestions: list[dict] = []
    desktop = context.get("desktop", {})
    active = desktop.get("active_window", {})
    app_name = active.get("app", "")
    if "code" in str(app_name).lower() or "vscode" in str(app_name).lower():
        suggestions.append(
            {
                "id": str(uuid4()),
                "title": "Run tests",
                "message": "Consider running project tests before committing.",
                "confidence": 0.7,
            }
        )
    if hasattr(app, "proactive") and app.settings.proactive_recommendations_enabled:
        recs = getattr(app.proactive, "_recommendations", [])
        for r in list(recs)[-3:]:
            suggestions.append(
                {
                    "id": getattr(r, "id", str(uuid4())),
                    "title": getattr(r, "title", "Suggestion"),
                    "message": getattr(r, "message", ""),
                    "confidence": getattr(r, "confidence", 0.5),
                }
            )
    perception = context.get("summary", "")
    if "memory pressure" in perception.lower():
        suggestions.append(
            {
                "id": str(uuid4()),
                "title": "Reduce load",
                "message": "System memory is elevated — defer heavy missions.",
                "confidence": 0.8,
            }
        )
    if hasattr(app, "action_runtime") and getattr(app.settings, "action_engine_enabled", False):
        for s in suggestions[:2]:
            s["executable"] = True
            s["propose_kind"] = "suggest_followup"
    return suggestions[:5]
