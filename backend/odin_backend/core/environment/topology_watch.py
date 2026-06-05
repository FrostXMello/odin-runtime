"""Monitor distributed worker topology."""

from __future__ import annotations

from typing import Any


async def check_topology(app: Any) -> list[dict[str, Any]]:
    alerts: list[dict] = []
    registry = getattr(app, "worker_registry", None)
    if not registry:
        return alerts
    snap = registry.snapshot() if hasattr(registry, "snapshot") else {}
    workers = snap.get("workers", []) if isinstance(snap, dict) else []
    disconnected = [w for w in workers if w.get("status") == "disconnected"]
    if disconnected:
        alerts.append(
            {
                "kind": "worker_disconnected",
                "severity": "high",
                "message": f"{len(disconnected)} worker(s) disconnected",
            }
        )
    return alerts
