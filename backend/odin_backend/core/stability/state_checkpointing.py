"""Runtime state checkpoint snapshots."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class StateCheckpointing:
    def __init__(self) -> None:
        self._checkpoints: list[dict[str, Any]] = []

    def create(self, *, label: str, state: dict[str, Any]) -> dict[str, Any]:
        ckpt = {
            "id": str(uuid4()),
            "label": label,
            "state": state,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._checkpoints.append(ckpt)
        if len(self._checkpoints) > 50:
            self._checkpoints = self._checkpoints[-50:]
        return ckpt

    def latest(self) -> dict[str, Any] | None:
        return self._checkpoints[-1] if self._checkpoints else None

    def rollback(self, checkpoint_id: str) -> dict[str, Any] | None:
        for ckpt in reversed(self._checkpoints):
            if ckpt["id"] == checkpoint_id:
                return ckpt["state"]
        return None

    def list_all(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._checkpoints[-limit:]
