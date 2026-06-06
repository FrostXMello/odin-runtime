"""Permission audit log."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class PermissionAudit:
    def __init__(self) -> None:
        self._log: list[dict[str, Any]] = []

    def record(self, *, action: str, allowed: bool, reason: str = "") -> None:
        self._log.append({
            "action": action,
            "allowed": allowed,
            "reason": reason,
            "at": datetime.now(timezone.utc).isoformat(),
        })

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._log[-limit:]
