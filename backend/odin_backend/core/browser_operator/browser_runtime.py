"""Supervised browser operator runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.browser_operator.browser_actions import fill_form, navigate
from odin_backend.core.browser_operator.browser_sessions import BrowserSessionStore
from odin_backend.core.browser_operator.tab_memory import TabMemory


class BrowserOperatorRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._sessions = BrowserSessionStore()
        self._tabs = TabMemory()

    async def start_session(self) -> dict[str, Any]:
        sess = self._sessions.start()
        self._emit("browser_navigation", {"event": "session_started", "session_id": sess["id"]})
        intelligence = getattr(self._app, "browser", None)
        if intelligence:
            try:
                tabs = await intelligence.get_active_tabs()
                for t in tabs[:10]:
                    self._tabs.record({"url": getattr(t, "url", str(t)), "title": getattr(t, "title", "")})
            except Exception:
                pass
        return sess

    async def execute_action(self, kind: str, payload: dict[str, Any]) -> dict[str, Any]:
        if kind in ("navigate", "browser_navigate"):
            result = await navigate(self._app, url=str(payload.get("url", "")))
            if not result.get("blocked"):
                self._emit("browser_navigation", {"url": payload.get("url")})
            return result
        if kind in ("fill_form", "browser_fill"):
            return await fill_form(self._app, selector=str(payload.get("selector", "")), value=str(payload.get("value", "")))
        return {"error": "unsupported_browser_action", "kind": kind}

    def snapshot(self) -> dict[str, Any]:
        active = self._sessions.active()
        return {
            "active_session": active,
            "sessions": self._sessions.list_all(),
            "recent_tabs": self._tabs.recent()[-10:],
            "enabled": getattr(self._app.settings, "browser_operator_enabled", False),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="browser_operator")
