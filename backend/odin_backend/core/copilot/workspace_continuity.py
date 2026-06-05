"""Workspace continuity and session restoration."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class WorkspaceContinuity:
    def __init__(self) -> None:
        self._snapshots: list[dict[str, Any]] = []

    def capture(self, *, workspace: dict[str, Any]) -> dict[str, Any]:
        snap = {
            "id": str(uuid4()),
            "workspace": workspace,
            "captured_at": datetime.now(timezone.utc).isoformat(),
        }
        self._snapshots.append(snap)
        if len(self._snapshots) > 30:
            self._snapshots = self._snapshots[-30:]
        return snap

    def restore_latest(self) -> dict[str, Any] | None:
        return self._snapshots[-1] if self._snapshots else None

    def list_snapshots(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._snapshots[-limit:]
