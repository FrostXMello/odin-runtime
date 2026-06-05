"""Operator interaction memory."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class InteractionMemory:
    def __init__(self) -> None:
        self._interactions: list[dict[str, Any]] = []

    def record(self, *, kind: str, detail: str) -> dict[str, Any]:
        entry = {"kind": kind, "detail": detail, "at": datetime.now(timezone.utc).isoformat()}
        self._interactions.append(entry)
        return entry

    def recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._interactions[-limit:]
