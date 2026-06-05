"""Route actions to automation, browser, or simulation handlers."""

from __future__ import annotations

from typing import Any


async def dispatch_action(app: Any, action: dict[str, Any]) -> dict[str, Any]:
    kind = action.get("kind", "")
    payload = action.get("payload", {})
    simulation = getattr(app.settings, "automation_simulation_mode", True)

    if simulation:
        return {"simulated": True, "kind": kind, "payload": payload}

    if kind.startswith("browser_") or kind in ("navigate", "fill_form", "click_element"):
        browser = getattr(app, "browser_operator", None)
        if browser:
            return await browser.execute_action(kind, payload)
        return {"error": "browser_operator_unavailable"}

    automation = getattr(app, "automation_sandbox", None)
    if automation and kind in ("click", "mouse_move", "type_text", "key_press", "focus_window"):
        return await automation.execute(kind, payload)

    return {"error": "unknown_action_kind", "kind": kind}
