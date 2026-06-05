"""Desktop state snapshot for perception."""

from __future__ import annotations

from typing import Any


class DesktopState:
    def __init__(self) -> None:
        self._active_window: dict[str, Any] = {}
        self._apps: list[str] = []
        self._last_snapshot: dict[str, Any] = {}

    def apply_snapshot(self, snapshot: dict[str, Any]) -> None:
        self._last_snapshot = snapshot
        self._active_window = snapshot.get("active_window") or {}
        apps = snapshot.get("running_apps") or snapshot.get("apps") or []
        if isinstance(apps, list):
            self._apps = [str(a) for a in apps[:20]]

    def snapshot(self) -> dict[str, Any]:
        return {
            "active_window": self._active_window,
            "apps": self._apps,
            "field_count": len(self._last_snapshot),
        }
