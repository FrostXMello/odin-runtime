"""Node heartbeat and presence tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class FederationPresence:
    def __init__(self) -> None:
        self._heartbeats: dict[str, str] = {}

    def heartbeat(self, node_id: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat()
        self._heartbeats[node_id] = now
        return {"node_id": node_id, "last_heartbeat": now, "status": "online"}

    def is_stale(self, node_id: str, *, max_age_seconds: int = 120) -> bool:
        ts = self._heartbeats.get(node_id)
        if not ts:
            return True
        last = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - last).total_seconds()
        return age > max_age_seconds

    def snapshot(self) -> dict[str, Any]:
        return {"nodes_online": len(self._heartbeats), "heartbeats": dict(self._heartbeats)}
