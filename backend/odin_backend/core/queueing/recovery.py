"""Distributed startup recovery coordinator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.observability.events import TraceEventKind
from odin_backend.core.execution.models import ExecutionState
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_UNRECOVERABLE = {ExecutionState.FAILED, ExecutionState.CANCELLED, ExecutionState.TIMED_OUT}


class DistributedRecoveryCoordinator:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._metrics: dict[str, int] = {
            "queue_restored": 0,
            "leases_recovered": 0,
            "executions_recovered": 0,
            "orphans_detected": 0,
            "tasks_requeued": 0,
            "deadlettered": 0,
            "replay_suppressed": 0,
            "workers_disconnected": 0,
            "leases_fenced": 0,
            "distributed_requeues": 0,
            "topology_recovered": 0,
        }

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    async def recover_on_startup(self) -> dict[str, Any]:
        obs = getattr(self._app, "observability", None)
        results: dict[str, Any] = {}

        q = getattr(self._app, "distributed_queue", None)
        if q:
            requeued = await q.requeue_expired()
            self._metrics["leases_recovered"] = requeued
            self._metrics["tasks_requeued"] = requeued
            self._metrics["distributed_requeues"] = requeued
            if requeued and obs:
                obs.tracer.record(
                    TraceEventKind.DISTRIBUTED_REQUEUE,
                    message=f"requeued {requeued} expired leases",
                    payload={"count": requeued},
                    component="distributed_recovery",
                )
                obs.tracer.record(
                    TraceEventKind.LEASE_RECOVERED,
                    message=f"requeued {requeued} expired leases",
                    component="distributed_recovery",
                )

            stats = await q.stats()
            self._metrics["queue_restored"] = stats.get("total", 0)
            if obs:
                obs.tracer.record(
                    TraceEventKind.QUEUE_RESTORED,
                    message="queue state restored",
                    payload=stats,
                    component="distributed_recovery",
                )
            results["queue"] = stats

        await self._recover_stale_workers(obs)
        await self._recover_topology(obs, results)

        if self._app.settings.execution_persist_enabled:
            store = self._app.execution_engine.store
            if hasattr(store, "hydrate"):
                count = await store.hydrate()
                self._metrics["executions_recovered"] = count
                if count and obs:
                    obs.tracer.record(
                        TraceEventKind.EXECUTION_RECOVERED,
                        message=f"hydrated {count} executions",
                        component="distributed_recovery",
                    )
                results["executions_hydrated"] = count

        if hasattr(self._app, "execution_reconciliation"):
            rec = await self._app.execution_reconciliation.reconcile_on_startup()
            self._metrics["orphans_detected"] = rec.get("orphan_tasks_repaired", 0)
            results["execution_reconciliation"] = rec

        if q and q.deadletter:
            dl = await q.deadletter.list_items(limit=100)
            self._metrics["deadlettered"] = len(dl)
            results["deadletters"] = len(dl)

        self._metrics["replay_suppressed"] = q.wake_signals.replay_suppressed if q else 0
        results["metrics"] = self._metrics
        logger.info("distributed_recovery_complete", **self._metrics)
        return results

    async def _recover_stale_workers(self, obs: Any) -> int:
        reg = getattr(self._app, "worker_registry", None)
        if not reg:
            return 0
        workers = await reg.list_workers(stale_seconds=120.0)
        stale = [w for w in workers if w.get("stale")]
        if not stale:
            return 0
        self._metrics["workers_disconnected"] = len(stale)
        if obs:
            for w in stale:
                obs.tracer.record(
                    TraceEventKind.WORKER_DISCONNECTED,
                    message=f"stale worker {w['worker_id']}",
                    payload=w,
                    component="distributed_recovery",
                )
        return len(stale)

    async def _recover_topology(self, obs: Any, results: dict[str, Any]) -> None:
        topo = getattr(self._app, "runtime_topology", None)
        if not topo:
            return
        snap = await topo.snapshot()
        self._metrics["topology_recovered"] = snap.get("worker_count", 0)
        results["topology"] = {
            "worker_count": snap.get("worker_count"),
            "transport": snap.get("transport"),
        }
        if obs:
            obs.tracer.record(
                TraceEventKind.TOPOLOGY_RECOVERED,
                message="topology snapshot recovered",
                payload=results["topology"],
                component="distributed_recovery",
            )

    async def recover_abandoned_leases(self) -> int:
        q = getattr(self._app, "distributed_queue", None)
        if not q:
            return 0
        count = await q.requeue_expired()
        self._metrics["leases_fenced"] += count
        obs = getattr(self._app, "observability", None)
        if count and obs:
            obs.tracer.record(
                TraceEventKind.LEASE_FENCED,
                message=f"fenced {count} abandoned leases",
                payload={"count": count},
                component="distributed_recovery",
            )
        return count
