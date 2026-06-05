"""Observability-specific metrics (histograms, rates)."""

from __future__ import annotations

from typing import Any

from odin_backend.monitoring.metrics import MetricsCollector


class ObservabilityMetrics:
    def __init__(self, base: MetricsCollector | None = None) -> None:
        self._base = base or MetricsCollector()

    @property
    def collector(self) -> MetricsCollector:
        return self._base

    def record_mission_latency(self, seconds: float, *, mission_id: str = "") -> None:
        self._base.record_latency("observability.mission.latency", seconds, mission_id=mission_id[:8])

    def record_task_execution(self, seconds: float, *, tool: str = "noop", success: bool = True) -> None:
        self._base.record_latency(
            "observability.task.execution",
            seconds,
            tool=tool,
            success=str(success),
        )

    def record_retry(self, *, mission_id: str = "") -> None:
        self._base.increment("observability.retry", mission_id=mission_id[:8])

    def record_escalation(self, *, mission_id: str = "") -> None:
        self._base.increment("observability.escalation", mission_id=mission_id[:8])

    def record_signal_latency(self, ms: float) -> None:
        self._base.record_latency("observability.signal.propagation", ms / 1000.0)

    def record_memory_mutation(self, *, category: str = "general") -> None:
        self._base.increment("observability.memory.mutation", category=category)

    def record_dispatcher_pickup(self, seconds: float) -> None:
        self._base.record_latency("observability.dispatcher.pickup", seconds)

    def record_queue_wait(self, seconds: float) -> None:
        self._base.record_latency("observability.queue.wait", seconds)

    def record_agent_utilization(self, agent_id: str, active: bool) -> None:
        self._base.increment(
            "observability.agent.utilization",
            agent_id=agent_id,
            active=str(active),
        )

    def snapshot(self) -> dict[str, Any]:
        snap = self._base.snapshot()
        lat = snap.get("latency_avg", {})
        return {
            **snap,
            "observability_latency": {
                k: {"avg": v}
                for k, v in lat.items()
                if k.startswith("observability.")
            },
        }


def _hist_summary(values: list[float]) -> dict[str, float]:
    if not values:
        return {"count": 0, "p50": 0, "p95": 0, "max": 0}
    s = sorted(values)
    n = len(s)
    return {
        "count": float(n),
        "p50": s[n // 2],
        "p95": s[int(n * 0.95)] if n > 1 else s[0],
        "max": s[-1],
    }
