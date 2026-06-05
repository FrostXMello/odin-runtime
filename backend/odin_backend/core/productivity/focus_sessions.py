"""Focus session tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class FocusSessions:
    def __init__(self) -> None:
        self._active: dict[str, Any] | None = None
        self._history: list[dict[str, Any]] = []

    def start(self, *, label: str) -> dict[str, Any]:
        self._active = {"label": label, "started_at": datetime.now(timezone.utc).isoformat()}
        return self._active

    def stop(self) -> dict[str, Any] | None:
        if not self._active:
            return None
        ended = {**self._active, "ended_at": datetime.now(timezone.utc).isoformat()}
        self._history.append(ended)
        self._active = None
        return ended
