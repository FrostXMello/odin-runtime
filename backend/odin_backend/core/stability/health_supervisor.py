"""Runtime health supervision."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class HealthSupervisor:
    def __init__(self) -> None:
        self._checks: list[dict[str, Any]] = []
        self._last_healthy: str | None = None

    def evaluate(self, *, loop_age_s: float, memory_pressure: str, stalled_loops: int) -> dict[str, Any]:
        healthy = stalled_loops == 0 and memory_pressure not in ("critical",)
        status = "healthy" if healthy else "degraded"
        if healthy:
            self._last_healthy = datetime.now(timezone.utc).isoformat()
        report = {
            "status": status,
            "loop_age_s": loop_age_s,
            "memory_pressure": memory_pressure,
            "stalled_loops": stalled_loops,
            "last_healthy": self._last_healthy,
        }
        self._checks.append(report)
        if len(self._checks) > 100:
            self._checks = self._checks[-100:]
        return report

    def history(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._checks[-limit:]
