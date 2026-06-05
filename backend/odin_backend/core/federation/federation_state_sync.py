"""Federation state synchronization."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class FederationStateSync:
    def __init__(self) -> None:
        self._versions: dict[str, int] = {}
        self._snapshots: dict[str, dict[str, Any]] = {}

    def push(self, node_id: str, state: dict[str, Any]) -> dict[str, Any]:
        version = self._versions.get(node_id, 0) + 1
        self._versions[node_id] = version
        self._snapshots[node_id] = {
            "version": version,
            "state": state,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._snapshots[node_id]

    def get(self, node_id: str) -> dict[str, Any] | None:
        return self._snapshots.get(node_id)

    def versions(self) -> dict[str, int]:
        return dict(self._versions)
