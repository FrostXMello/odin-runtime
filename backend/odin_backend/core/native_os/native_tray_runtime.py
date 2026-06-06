from __future__ import annotations
from typing import Any


class NativeTrayRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._visible = False

    async def show(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_os_enabled", False):
            return {"accepted": False, "reason": "native_os_disabled"}
        self._visible = True
        return {"accepted": True, "tray_visible": True, "bounded": True}

    def snapshot(self) -> dict[str, Any]:
        return {"visible": self._visible}
