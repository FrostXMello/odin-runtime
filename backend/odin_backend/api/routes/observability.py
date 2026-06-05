"""Observability API — traces, audit logs, causal events."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/traces")
async def list_traces(request: Request, limit: int = 50) -> dict:
    app = request.app.state.odin
    legacy = app.trace_manager.list_recent(limit)
    causal = [
        e.model_dump(mode="json")
        for e in app.observability.tracer.store.recent(limit)
    ]
    return {
        "execution_traces": legacy,
        "causal_events": causal,
        "store_stats": app.observability.tracer.store.stats(),
    }


@router.get("/causal-events")
async def causal_events(request: Request, limit: int = 100) -> list[dict]:
    app = request.app.state.odin
    return [e.model_dump(mode="json") for e in app.observability.tracer.store.recent(limit)]


@router.get("/memory-mutations")
async def memory_mutations(request: Request, limit: int = 50) -> list[dict]:
    app = request.app.state.odin
    return app.observability.memory_audit.recent(limit)


@router.get("/audit")
async def list_audit(request: Request, limit: int = 100) -> list[dict]:
    app = request.app.state.odin
    return app.audit_logger.get_recent(limit)


@router.get("/events/recent")
async def recent_events(request: Request, limit: int = 100) -> list[dict]:
    app = request.app.state.odin
    return app.event_hub.recent(limit)


@router.get("/metrics")
async def metrics_snapshot(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "runtime": app.metrics.snapshot(),
        "observability": app.observability.metrics.snapshot(),
    }
