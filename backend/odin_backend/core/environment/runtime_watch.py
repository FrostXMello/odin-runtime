"""Monitor runtime health signals."""

from __future__ import annotations

from typing import Any


async def check_runtime(app: Any) -> list[dict[str, Any]]:
    alerts: list[dict] = []
    if hasattr(app, "failure_intelligence"):
        report = await app.failure_intelligence.analyze()
        if report.oscillation_detected:
            alerts.append(
                {
                    "kind": "mission_oscillation",
                    "severity": "high",
                    "message": "Mission retry/replan oscillation detected",
                }
            )
        if report.degraded_capabilities:
            alerts.append(
                {
                    "kind": "degraded_capabilities",
                    "severity": "medium",
                    "message": f"Degraded: {', '.join(report.degraded_capabilities[:3])}",
                }
            )
    return alerts
