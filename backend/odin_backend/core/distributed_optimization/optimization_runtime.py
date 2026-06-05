"""Distributed infrastructure optimization orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.distributed_optimization.adaptive_replication import replication_factor
from odin_backend.core.distributed_optimization.distributed_reasoning_allocator import allocate
from odin_backend.core.distributed_optimization.federation_efficiency import measure
from odin_backend.core.distributed_optimization.node_specialization import recommend
from odin_backend.core.distributed_optimization.topology_optimizer import optimize_topology
from odin_backend.core.distributed_optimization.workload_balancer import balance


class DistributedOptimizationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def optimize(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "distributed_optimization_enabled", False):
            return {"accepted": False, "reason": "distributed_optimization_disabled"}
        fed = getattr(self._app, "federation_runtime", None)
        nodes = await fed.list_nodes() if fed else []
        topo = fed.topology() if fed else {"edge_count": 0, "node_count": 0}
        topo_opt = optimize_topology(edge_count=topo.get("edge_count", 0), node_count=topo.get("node_count", 0))
        loads = {n["node_id"]: n.get("active_mission_count", 0) for n in nodes}
        balanced = balance(loads)
        placement = allocate(nodes)
        efficiency = measure(successful=len(nodes), total=max(len(nodes), 1), avg_latency=50.0)
        specs = recommend(nodes)
        repl = replication_factor(trust=0.6, load=0.4)
        self._emit("workload_rebalanced", balanced)
        return {
            "accepted": True,
            "topology": topo_opt,
            "workload": balanced,
            "placement": placement,
            "efficiency": efficiency,
            "specializations": specs,
            "replication_factor": repl,
        }

    def snapshot(self) -> dict[str, Any]:
        return {"status": "ready", "enabled": getattr(self._app.settings, "distributed_optimization_enabled", False)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="distributed_optimization")
