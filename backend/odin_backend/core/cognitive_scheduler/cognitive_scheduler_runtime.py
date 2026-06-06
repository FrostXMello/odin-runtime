"""Cognitive scheduler (Prompt 52)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.cognitive_scheduler.task_queues import TaskQueues


class CognitiveSchedulerRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queues = TaskQueues()
        self._cooldown_s = 0.0
        self._budget = 1.0

    async def schedule_cognition(self, *, task: str, queue: str = "active") -> dict[str, Any]:
        if not getattr(self._app.settings, "cognitive_scheduler_enabled", False):
            return {"accepted": False, "reason": "cognitive_scheduler_disabled"}
        q = getattr(self._queues, queue, self._queues.active)
        q.append(task[:120])
        return {"accepted": True, "queue": queue, "size": len(q), "budget": self._budget}

    async def defer_task(self, *, task: str) -> dict[str, Any]:
        self._queues.defer(task)
        if hasattr(self._app, "autonomous_loop_v2"):
            await self._app.autonomous_loop_v2.defer_task(task=task)
        return {"accepted": True, "deferred": True, "approval_required": True}

    async def restore_deferred_tasks(self) -> dict[str, Any]:
        restored = self._queues.restore()
        if restored:
            self._emit("deferred_task_restored", {"count": len(restored)})
        return {"accepted": True, "restored": restored}

    async def rebalance_runtime_load(self) -> dict[str, Any]:
        if hasattr(self._app, "adaptive_runtime"):
            await self._app.adaptive_runtime.scale(load=0.5)
        if hasattr(self._app, "cognitive_load_balancer"):
            await self._app.cognitive_load_balancer.balance(load=0.5)
        self._emit("runtime_load_rebalanced", {"rebalanced": True})
        return {"accepted": True, "rebalanced": True, "cooldown_s": self._cooldown_s}

    def snapshot(self) -> dict[str, Any]:
        return {
            "active": len(self._queues.active),
            "background": len(self._queues.background),
            "deferred": len(self._queues.deferred),
            "overnight": len(self._queues.overnight),
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="cognitive_scheduler")
