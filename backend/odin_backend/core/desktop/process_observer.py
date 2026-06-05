"""Process/app usage observation."""

from __future__ import annotations

from typing import Any


class ProcessObserver:
    def __init__(self) -> None:
        self._usage: dict[str, int] = {}

    def observe(self, snapshot: dict[str, Any]) -> dict[str, int]:
        apps = snapshot.get("running_apps") or snapshot.get("apps") or []
        for app in apps[:30]:
            key = str(app)
            self._usage[key] = self._usage.get(key, 0) + 1
        return dict(self._usage)
