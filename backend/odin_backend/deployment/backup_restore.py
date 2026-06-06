"""Backup and restore."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


class BackupRestore:
    def __init__(self) -> None:
        self._snapshots: dict[str, dict[str, Any]] = {}

    def export_state(self, state: dict[str, Any]) -> dict[str, Any]:
        sid = str(uuid4())
        self._snapshots[sid] = state
        return {"snapshot_id": sid, "exported": True}

    def import_state(self, snapshot_id: str) -> dict[str, Any] | None:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> list[str]:
        return list(self._snapshots.keys())
