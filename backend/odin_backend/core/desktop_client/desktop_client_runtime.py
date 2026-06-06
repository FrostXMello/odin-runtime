"""Desktop client session orchestrator."""
from __future__ import annotations
from typing import Any

from odin_backend.core.desktop_client.session_store import load_session, save_session

MODES = ("compact", "balanced", "immersive", "cinematic")


class DesktopClientRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = getattr(app.settings, "native_desktop_mode", "balanced")
        self._session_path = "./data/desktop_session.json"

    async def connect(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "desktop_client_enabled", False):
            return {"accepted": False, "reason": "desktop_client_disabled"}
        restored = load_session(path=self._session_path)
        if restored.get("restored"):
            self._emit("desktop_session_restored", {"mode": self._mode})
        return {
            "accepted": True,
            "mode": self._mode,
            "modes": list(MODES),
            "local_backend": True,
            "session": restored,
        }

    async def set_mode(self, mode: str) -> dict[str, Any]:
        if mode not in MODES:
            return {"accepted": False, "reason": "invalid_mode"}
        self._mode = mode
        save_session(path=self._session_path, data={"mode": mode})
        return {"accepted": True, "mode": mode, "fps_cap": {"compact": 15, "balanced": 30, "immersive": 45, "cinematic": 60}.get(mode, 30)}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "modes": list(MODES)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="desktop_client")
