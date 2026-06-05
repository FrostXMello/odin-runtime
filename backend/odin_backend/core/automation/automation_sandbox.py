"""Sandboxed desktop automation executor."""

from __future__ import annotations

from typing import Any

from odin_backend.core.automation.interaction_guard import InteractionGuard
from odin_backend.core.automation.keyboard_controller import key_press, type_text
from odin_backend.core.automation.mouse_controller import mouse_click, mouse_move
from odin_backend.core.automation.window_controller import focus_window


class AutomationSandbox:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._guard = InteractionGuard(app)

    async def execute(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        allowed, reason = self._guard.allow()
        if not allowed:
            return {"blocked": True, "reason": reason}
        if kind == "click":
            return await mouse_click(self._app, x=int(payload.get("x", 0)), y=int(payload.get("y", 0)))
        if kind == "mouse_move":
            return await mouse_move(self._app, x=int(payload.get("x", 0)), y=int(payload.get("y", 0)))
        if kind == "type_text":
            return await type_text(self._app, text=str(payload.get("text", "")))
        if kind == "key_press":
            return await key_press(self._app, key=str(payload.get("key", "")))
        if kind == "focus_window":
            return await focus_window(self._app, title=str(payload.get("title", "")))
        return {"error": "unsupported_automation_kind", "kind": kind}
