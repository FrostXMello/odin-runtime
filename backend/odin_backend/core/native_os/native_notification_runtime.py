from __future__ import annotations
from typing import Any


class NativeNotificationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue: list[dict] = []

    async def notify(self, *, title: str, body: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "native_os_enabled", False):
            return {"accepted": False, "reason": "native_os_disabled"}
        item = {"title": title[:80], "body": body[:240], "routed": True}
        self._queue.append(item)
        return {"accepted": True, "notification": item, "approval_gated": False}

    def snapshot(self) -> dict[str, Any]:
        return {"queued": len(self._queue)}
