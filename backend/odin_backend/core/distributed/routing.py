"""Capability-aware worker routing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DEFAULT_CAPABILITIES = frozenset(
    {
        "python.safe",
        "shell.safe",
        "workflow.execute",
        "filesystem.read",
        "filesystem.write",
        "api.internal",
        "api.*",
        "browser.*",
    }
)


@dataclass
class WorkerRouteTarget:
    worker_id: str
    capabilities: set[str] = field(default_factory=set)
    active_leases: int = 0
    concurrency: int = 4
    stale: bool = False
    score: float = 0.0


class CapabilityRouter:
    """Select workers for capability execution with load balancing."""

    def __init__(self, app: Any | None = None) -> None:
        self._app = app
        self._decisions: list[dict[str, Any]] = []

    async def list_targets(self) -> list[WorkerRouteTarget]:
        if not self._app:
            return []
        reg = getattr(self._app, "worker_registry", None)
        if not reg:
            return []
        workers = await reg.list_workers()
        out: list[WorkerRouteTarget] = []
        for w in workers:
            caps = set(w.get("capabilities") or [])
            if not caps:
                caps = set(DEFAULT_CAPABILITIES)
            out.append(
                WorkerRouteTarget(
                    worker_id=w["worker_id"],
                    capabilities=caps,
                    active_leases=int(w.get("active_leases") or 0),
                    concurrency=int(w.get("concurrency") or 4),
                    stale=bool(w.get("stale")),
                )
            )
        return out

    def _score(self, target: WorkerRouteTarget, capability: str) -> float:
        if target.stale:
            return -1.0
        if not self._matches(capability, target.capabilities):
            return -1.0
        util = target.active_leases / max(1, target.concurrency)
        return 100.0 - util * 50.0 - target.active_leases * 2.0

    @staticmethod
    def _matches(capability: str, caps: set[str]) -> bool:
        if capability in caps:
            return True
        prefix = capability.split(".")[0]
        return f"{prefix}.*" in caps or "api.*" in caps

    async def route(self, capability: str) -> WorkerRouteTarget | None:
        targets = await self.list_targets()
        best: WorkerRouteTarget | None = None
        best_score = -1.0
        for t in targets:
            t.score = self._score(t, capability)
            if t.score > best_score:
                best_score = t.score
                best = t
        decision = {
            "capability": capability,
            "worker_id": best.worker_id if best else None,
            "score": best_score,
        }
        self._decisions.append(decision)
        if self._app:
            obs = getattr(self._app, "observability", None)
            if obs:
                from odin_backend.core.observability.events import TraceEventKind

                obs.tracer.record(
                    TraceEventKind.ROUTING_DECISION,
                    message=f"route {capability}",
                    payload=decision,
                    component="capability_router",
                )
        return best

    @property
    def recent_decisions(self) -> list[dict[str, Any]]:
        return self._decisions[-50:]
