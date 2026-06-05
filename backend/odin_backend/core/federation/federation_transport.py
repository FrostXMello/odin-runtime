"""Local-first federation transport (no unrestricted internet)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class FederationTransport:
    """In-process transport for trusted local/cluster nodes."""

    def __init__(self) -> None:
        self._pending: list[dict[str, Any]] = []
        self._delivered: list[dict[str, Any]] = []

    def send(self, *, from_node: str, to_node: str, kind: str, payload: dict) -> dict[str, Any]:
        msg = {
            "id": str(uuid4()),
            "from_node": from_node,
            "to_node": to_node,
            "kind": kind,
            "payload": payload,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "delivered",
        }
        self._pending.append(msg)
        self._delivered.append(msg)
        return msg

    def receive(self, node_id: str) -> list[dict[str, Any]]:
        return [m for m in self._delivered if m["to_node"] == node_id]

    def pending_count(self) -> int:
        return len(self._pending)
