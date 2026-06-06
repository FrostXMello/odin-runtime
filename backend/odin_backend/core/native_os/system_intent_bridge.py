"""System intent bridge (Prompt 50)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.native_os.file_intent_router import route


class SystemIntentBridge:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def dispatch(self, *, intent: str, payload: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "native_os_enabled", False):
            return {"accepted": False, "reason": "native_os_disabled"}
        routed = route(path=payload or intent, action=intent[:40])
        return {"accepted": True, "intent": intent[:80], "routed": routed, "supervised": True}

    async def open_file(self, *, path: str) -> dict[str, Any]:
        return await self.dispatch(intent="open_file", payload=path)

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": True}
