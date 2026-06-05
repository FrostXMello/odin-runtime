"""Runtime diagnostics — health, recursion, signal throughput."""

from fastapi import APIRouter, Request

from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.core.missions.health import assess_orchestration_health
from odin_backend.core.observability.diagnostics import analyze_runtime

router = APIRouter(prefix="/runtime", tags=["runtime-diagnostics"])


def _bus_metrics(app) -> dict:
    bus = app.event_bus
    if isinstance(bus, SignalUnificationBus):
        return bus.runtime_metrics()
    return {
        "recursion_events_detected": 0,
        "suppressed_signal_count": 0,
        "runtime_loop_health": "unknown",
        "active_signal_chains": 0,
        "kernel_processing_rate": 0.0,
        "total_published": 0,
        "kernel_processed": 0,
        "internal_bypassed": 0,
        "in_flight": 0,
        "kernel_in_flight": 0,
    }


@router.get("/dependencies")
async def runtime_dependencies(request: Request) -> dict:
    app = request.app.state.odin
    graphs = []
    for mid in list(app.mission_manager._active.keys())[:15]:  # noqa: SLF001
        mission = await app.mission_manager.get(mid)
        if mission:
            graphs.append(app.mission_execution_bridge.planner.dependency_snapshot(mission))
    return {"mission_count": len(graphs), "graphs": graphs}


@router.get("/executions")
async def runtime_executions(request: Request, limit: int = 100) -> dict:
    engine = request.app.state.odin.execution_engine
    records = await engine.list_executions(limit=limit)
    active_missions = [
        {
            "mission_id": r.mission_id,
            "task_id": r.task_id,
            "execution_id": r.execution_id,
            "state": r.state.value,
        }
        for r in records
        if r.mission_id and r.state.value in ("running", "allocated", "queued", "retrying")
    ]
    return {
        "count": len(records),
        "metrics": engine.metrics.snapshot(),
        "executions": [r.model_dump(mode="json") for r in records],
        "active_mission_executions": active_missions,
    }


@router.get("/health")
async def runtime_health(request: Request) -> dict:
    app = request.app.state.odin
    state = app.kernel.get_state()
    metrics = _bus_metrics(app)
    mission_diag = app.mission_manager.diagnostics()
    rt_metrics = app.mission_runtime.metrics
    orchestration = assess_orchestration_health(app)
    root_cause = analyze_runtime(app)
    dispatcher_metrics = (
        app.mission_dispatcher.metrics if hasattr(app, "mission_dispatcher") else {}
    )
    gc_stats = app.mission_gc.stats if hasattr(app, "mission_gc") else {}

    system_health = state.system_health
    if orchestration.status == "critical" or root_cause.status == "critical":
        system_health = "critical"
    elif (
        orchestration.status == "degraded"
        or root_cause.status == "degraded"
    ) and system_health == "healthy":
        system_health = "degraded"

    return {
        "status": app.runtime.get_status(),
        "system_health": system_health,
        "orchestration": orchestration.model_dump(),
        "root_cause_analysis": root_cause.model_dump(),
        "missions": {
            **mission_diag,
            "queue_depth": app.mission_worker.scheduler.backlog_depth(),
            "dispatcher": dispatcher_metrics,
            "gc": gc_stats,
            "runtime_metrics": rt_metrics,
            "planner_health": "ok",
        },
        "runtime_loop_health": metrics.get("runtime_loop_health", state.runtime_loop_health),
        "recursion_events_detected": metrics.get("recursion_events_detected", 0),
        "suppressed_signal_count": metrics.get("suppressed_signal_count", 0),
        "kernel_processing_rate": metrics.get("kernel_processing_rate", 0.0),
        "active_signal_chains": metrics.get("active_signal_chains", 0),
        "signal_count": state.signal_count,
    }


@router.get("/orchestration")
async def orchestration_health(request: Request) -> dict:
    app = request.app.state.odin
    report = assess_orchestration_health(app)
    return report.model_dump()


@router.get("/recursion")
async def runtime_recursion(request: Request) -> dict:
    app = request.app.state.odin
    bus = app.event_bus
    if not isinstance(bus, SignalUnificationBus):
        return {"guard_enabled": False, "metrics": {}, "suppressed_loops": [], "active_chains": []}
    guard = bus.recursion_guard
    metrics = guard.metrics
    return {
        "guard_enabled": True,
        "current_depth": guard.current_depth,
        "metrics": metrics.model_dump(),
        "suppressed_loops": metrics.suppressed_loops,
        "active_chains": metrics.active_chains,
    }


@router.get("/signals")
async def runtime_signals(request: Request) -> dict:
    app = request.app.state.odin
    bus = app.event_bus
    metrics = _bus_metrics(app)
    state = app.kernel.get_state()
    queue_status = {
        "in_flight": metrics.get("in_flight", 0),
        "kernel_in_flight": metrics.get("kernel_in_flight", 0),
        "priority_queue_size": len(state.priority_queue),
    }
    return {
        "throughput": {
            "total_published": metrics.get("total_published", 0),
            "kernel_processed": metrics.get("kernel_processed", 0),
            "internal_bypassed": metrics.get("internal_bypassed", 0),
            "kernel_processing_rate": metrics.get("kernel_processing_rate", 0.0),
        },
        "kernel_queue": queue_status,
        "active_signals": state.active_signals[-10:],
        "recent_kernel_signals": [s.model_dump(mode="json") for s in app.kernel.recent_signals(10)],
    }
