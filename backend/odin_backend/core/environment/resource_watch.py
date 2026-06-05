"""Monitor local resource pressure."""

from __future__ import annotations

from typing import Any

from odin_backend.core.resources.ram_monitor import memory_pressure, ram_status


async def check_resources(app: Any) -> list[dict[str, Any]]:
    alerts: list[dict] = []
    pressure = memory_pressure()
    ram = ram_status()
    if pressure > 0.85:
        alerts.append(
            {
                "kind": "memory_pressure",
                "severity": "critical",
                "message": f"RAM pressure {pressure:.0%}, available {ram.get('available_mb')}MB",
            }
        )
    elif pressure > 0.7:
        alerts.append(
            {
                "kind": "memory_pressure",
                "severity": "medium",
                "message": f"Elevated RAM pressure {pressure:.0%}",
            }
        )
    return alerts
