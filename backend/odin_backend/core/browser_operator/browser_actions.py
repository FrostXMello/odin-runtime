"""Controlled browser actions."""

from __future__ import annotations

from typing import Any

from odin_backend.core.browser_operator.navigation_guard import allow_navigation


async def navigate(app: Any, *, url: str) -> dict[str, Any]:
    ok, reason = allow_navigation(url)
    if not ok:
        return {"blocked": True, "reason": reason}
    if getattr(app.settings, "automation_simulation_mode", True):
        return {"simulated": True, "action": "navigate", "url": url}
    intelligence = getattr(app, "browser", None)
    if intelligence:
        tabs = await intelligence.get_active_tabs()
        return {"executed": True, "url": url, "tabs": len(tabs)}
    return {"simulated": True, "url": url}


async def fill_form(app: Any, *, selector: str, value: str) -> dict[str, Any]:
    if getattr(app.settings, "automation_simulation_mode", True):
        return {"simulated": True, "selector": selector, "value_length": len(value)}
    return {"simulated": True, "selector": selector}
