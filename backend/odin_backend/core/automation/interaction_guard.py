"""Rate limiting and approval gates for automation."""

from __future__ import annotations

import time
from typing import Any


class InteractionGuard:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._last_action = 0.0
        self._count_window: list[float] = []

    def allow(self) -> tuple[bool, str]:
        if getattr(self._app, "action_runtime", None) and self._app.action_runtime.emergency_stopped:
            return False, "emergency_stop_active"
        if not getattr(self._app.settings, "desktop_automation_enabled", False):
            return False, "desktop_automation_disabled"
        now = time.monotonic()
        min_gap = getattr(self._app.settings, "automation_min_gap_ms", 100) / 1000.0
        if now - self._last_action < min_gap:
            return False, "rate_limited"
        self._count_window = [t for t in self._count_window if now - t < 60.0]
        max_per_min = getattr(self._app.settings, "automation_max_per_minute", 30)
        if len(self._count_window) >= max_per_min:
            return False, "rate_limited"
        self._last_action = now
        self._count_window.append(now)
        return True, "ok"
