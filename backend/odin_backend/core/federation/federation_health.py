"""Federation health monitoring."""

from __future__ import annotations

from typing import Any


class FederationHealth:
    def __init__(self) -> None:
        self._checks: dict[str, dict[str, Any]] = {}

    def record(self, node_id: str, *, latency_ms: float, healthy: bool) -> dict[str, Any]:
        entry = {
            "node_id": node_id,
            "latency_ms": latency_ms,
            "healthy": healthy,
            "health_state": "healthy" if healthy else "degraded",
        }
        self._checks[node_id] = entry
        return entry

    def snapshot(self) -> dict[str, Any]:
        healthy = sum(1 for c in self._checks.values() if c.get("healthy"))
        return {
            "nodes_checked": len(self._checks),
            "healthy_count": healthy,
            "checks": list(self._checks.values())[-20:],
        }
