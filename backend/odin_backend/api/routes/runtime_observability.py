"""Live runtime introspection and diagnostics APIs."""

from fastapi import APIRouter, Request

from odin_backend.core.observability.introspection import (
    detect_bottlenecks,
    queue_snapshot,
    worker_snapshot,
)
from odin_backend.core.observability.diagnostics import analyze_runtime

router = APIRouter(prefix="/runtime", tags=["runtime-observability"])


@router.get("/introspection")
async def runtime_introspection(request: Request) -> dict:
    app = request.app.state.odin
    intro = app.observability.introspection_snapshot(app)
    diagnostics = analyze_runtime(app)
    return {
        "introspection": intro,
        "diagnostics": diagnostics.model_dump(),
        "metrics": app.observability.metrics.snapshot(),
    }


@router.get("/queues")
async def runtime_queues(request: Request) -> dict:
    app = request.app.state.odin
    from odin_backend.core.observability.introspection import queue_snapshot_async

    snap = await queue_snapshot_async(app)
    return snap.model_dump()


@router.get("/workers")
async def runtime_workers(request: Request) -> dict:
    app = request.app.state.odin
    from odin_backend.core.observability.introspection import worker_snapshot_async

    snap = await worker_snapshot_async(app)
    registry = app.agent_registry
    agents = []
    if hasattr(registry, "list_agents"):
        for agent in registry.list_agents():
            agents.append({"agent_id": str(getattr(agent, "agent_id", agent)), "status": "registered"})
    return {"workers": snap.model_dump(), "agents": agents}


@router.get("/bottlenecks")
async def runtime_bottlenecks(request: Request) -> dict:
    app = request.app.state.odin
    bottlenecks = detect_bottlenecks(app)
    return {
        "count": len(bottlenecks),
        "bottlenecks": [b.model_dump() for b in bottlenecks],
    }


@router.get("/signal-graph")
async def signal_graph_export(request: Request, limit: int = 500) -> dict:
    app = request.app.state.odin
    graph = app.observability.signal_graph.export_graph(limit_edges=limit)
    return graph.model_dump()
