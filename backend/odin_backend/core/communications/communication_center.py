"""Communication center aggregation."""

from __future__ import annotations

from typing import Any


class CommunicationCenter:
    def __init__(self) -> None:
        self._alerts: list[dict[str, Any]] = []

    def alert(self, *, kind: str, message: str) -> dict[str, Any]:
        entry = {"kind": kind, "message": message}
        self._alerts.append(entry)
        return entry

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._alerts[-limit:]
