"""HEIMDALL watcher — security anomaly detection."""

from typing import Any

from odin_backend.events.bus import EventBus
from odin_backend.models.task import AgentId
from odin_backend.monitoring.audit import AuditLogger
from odin_backend.watchers.base import BaseWatcher


class HeimdallWatcher(BaseWatcher):
    agent_id = AgentId.HEIMDALL
    name = "heimdall_security"

    def __init__(self, event_bus: EventBus, audit: AuditLogger, interval_seconds: int = 60) -> None:
        super().__init__(event_bus)
        self._audit = audit
        self.interval_seconds = interval_seconds

    async def observe(self) -> list[dict[str, Any]]:
        recent = self._audit.get_recent(30)
        denied = [e for e in recent if e.get("type") == "permission_check" and not e.get("allowed")]
        restricted = [e for e in recent if e.get("type") == "tool_execution" and not e.get("success")]

        insights: list[dict[str, Any]] = []
        if len(denied) >= 3:
            insights.append({
                "type": "security_anomaly",
                "summary": f"Elevated permission denials: {len(denied)} in recent window",
                "recommendation": "Review permission policies and pending approvals.",
                "severity": "medium",
                "action": "none",
            })
        if len(restricted) >= 2:
            insights.append({
                "type": "execution_anomaly",
                "summary": f"Multiple failed tool executions: {len(restricted)}",
                "recommendation": "Inspect tool logs and workflow traces.",
                "severity": "low",
                "action": "none",
            })
        return insights
