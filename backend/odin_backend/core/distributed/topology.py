"""Runtime topology graph for multi-node observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TopologyNode:
    node_id: str
    kind: str
    label: str
    status: str = "healthy"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TopologyEdge:
    source: str
    target: str
    kind: str = "flow"
    metadata: dict[str, Any] = field(default_factory=dict)


class RuntimeTopology:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def snapshot(self) -> dict[str, Any]:
        app = self._app
        nodes: list[TopologyNode] = []
        edges: list[TopologyEdge] = []

        dq = getattr(app, "distributed_queue", None)
        transport = app.settings.queue_backend if dq else "memory"
        worker_id = dq.worker_id if dq else "local"
        queue_health = {"status": "unknown"}
        if dq and hasattr(dq.backend, "health"):
            queue_health = await dq.backend.health()
        elif dq:
            queue_health = {"status": "healthy", "transport": transport}

        nodes.append(
            TopologyNode(
                node_id="control-plane",
                kind="control",
                label="Odin Control Plane",
                metadata={"worker_id": worker_id},
            )
        )
        nodes.append(
            TopologyNode(
                node_id=f"queue:{transport}",
                kind="queue",
                label=f"Queue ({transport})",
                status=queue_health.get("status", "unknown"),
                metadata=queue_health,
            )
        )
        edges.append(TopologyEdge("control-plane", f"queue:{transport}", kind="enqueue"))

        reg = getattr(app, "worker_registry", None)
        if reg:
            workers = await reg.list_workers()
            for w in workers:
                wid = w["worker_id"]
                nodes.append(
                    TopologyNode(
                        node_id=f"worker:{wid}",
                        kind="worker",
                        label=wid,
                        status="stale" if w.get("stale") else "healthy",
                        metadata=w,
                    )
                )
                edges.append(TopologyEdge(f"queue:{transport}", f"worker:{wid}", kind="dequeue"))

        pools = getattr(app, "execution_pool_manager", None)
        if pools:
            for name, metrics in pools.metrics.items():
                nodes.append(
                    TopologyNode(
                        node_id=f"pool:{name}",
                        kind="pool",
                        label=name,
                        metadata=metrics,
                    )
                )
                edges.append(TopologyEdge("control-plane", f"pool:{name}", kind="execute"))

        router = getattr(app, "capability_router", None)
        routing = router.recent_decisions if router else []

        stats = await dq.stats() if dq else {}
        return {
            "nodes": [n.__dict__ for n in nodes],
            "edges": [e.__dict__ for e in edges],
            "transport": transport,
            "queue_stats": stats,
            "routing_decisions": routing,
            "worker_count": len([n for n in nodes if n.kind == "worker"]),
        }
