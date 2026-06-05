"""Aggregate environmental awareness."""

from __future__ import annotations

from typing import Any

from odin_backend.core.environment import (
    external_signal_watch,
    filesystem_watch,
    resource_watch,
    runtime_watch,
    topology_watch,
)  # noqa: F401 — submodule watch handlers


class EnvironmentMonitor:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._alerts: list[dict] = []

    async def collect_alerts(self) -> list[dict[str, Any]]:
        alerts: list[dict] = []
        for check in (
            runtime_watch.check_runtime,
            topology_watch.check_topology,
            resource_watch.check_resources,
            filesystem_watch.check_filesystem,
            external_signal_watch.check_signals,
        ):
            try:
                alerts.extend(await check(self._app))
            except Exception:
                pass
        self._alerts = alerts
        for a in alerts:
            if a.get("severity") in ("high", "critical"):
                self._emit_alert(a)
        return alerts

    def recent_alerts(self) -> list[dict]:
        return list(self._alerts)

    def snapshot(self) -> dict:
        return {"alerts": self._alerts, "alert_count": len(self._alerts)}

    def _emit_alert(self, alert: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        obs.tracer.record(
            TraceEventKind.ENVIRONMENT_ALERT,
            message=alert.get("message", "environment alert"),
            payload=alert,
            component="environment_monitor",
        )
