"""Human approval chains for supervised actions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class ApprovalFlow:
    def __init__(self) -> None:
        self._pending: dict[str, dict[str, Any]] = {}
        self._resolved: list[dict[str, Any]] = []

    def request(self, *, action: str, detail: str, mission_id: str | None = None) -> dict[str, Any]:
        aid = str(uuid4())
        entry = {
            "id": aid,
            "action": action,
            "detail": detail[:1000],
            "mission_id": mission_id,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pending[aid] = entry
        return entry

    def resolve(self, approval_id: str, *, approved: bool, feedback: str = "") -> dict[str, Any] | None:
        entry = self._pending.pop(approval_id, None)
        if not entry:
            return None
        entry["status"] = "approved" if approved else "rejected"
        entry["feedback"] = feedback[:500]
        entry["resolved_at"] = datetime.now(timezone.utc).isoformat()
        self._resolved.append(entry)
        if len(self._resolved) > 100:
            self._resolved = self._resolved[-100:]
        return entry

    def pending(self) -> list[dict[str, Any]]:
        return list(self._pending.values())

    def history(self) -> list[dict[str, Any]]:
        return list(self._resolved)[-20:]
