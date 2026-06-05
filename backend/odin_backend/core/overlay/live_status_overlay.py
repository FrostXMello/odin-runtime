"""Live status overlay state."""

from __future__ import annotations

from typing import Any


class LiveStatusOverlay:
    def __init__(self) -> None:
        self._status = "idle"
        self._countdown: int | None = None

    def set_status(self, status: str, *, countdown: int | None = None) -> None:
        self._status = status
        self._countdown = countdown

    def snapshot(self) -> dict[str, Any]:
        return {"status": self._status, "countdown": self._countdown}
