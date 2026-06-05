"""Monitor internal signal anomalies (local-only, no internet)."""

from __future__ import annotations

from typing import Any


async def check_signals(app: Any) -> list[dict[str, Any]]:
    alerts: list[dict] = []
    queue = getattr(app, "distributed_queue", None)
    if queue and hasattr(queue, "metrics"):
        m = queue.metrics()
        dead = m.get("deadlettered", 0) if isinstance(m, dict) else 0
        if dead and dead > 5:
            alerts.append(
                {
                    "kind": "queue_anomaly",
                    "severity": "high",
                    "message": f"Deadletter count elevated: {dead}",
                }
            )
    return alerts
