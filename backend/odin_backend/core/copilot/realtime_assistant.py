"""Real-time desktop assistant."""

from __future__ import annotations

from typing import Any


async def assist(app: Any, *, context: dict) -> dict[str, Any]:
    app_name = context.get("active_app", "unknown")
    suggestions = []
    if "code" in app_name.lower() or "vscode" in app_name.lower():
        suggestions.append({"action": "explain_selection", "confidence": 0.7})
    if "browser" in app_name.lower():
        suggestions.append({"action": "summarize_page", "confidence": 0.6})
    return {"app": app_name, "suggestions": suggestions, "requires_approval": True}
