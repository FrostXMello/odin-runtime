"""Production hardening APIs (Prompt 64)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["production-hardening-runtime"])


class DiagnosticReportRequest(BaseModel):
    mode: str = "lightweight"


class CleanupRequest(BaseModel):
    mode: str = "passive"


@router.get("/runtime-diagnostics/health")
async def runtime_diagnostics_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_diagnostics.inspect_runtime_health()


@router.post("/runtime-diagnostics/report")
async def runtime_diagnostics_report(body: DiagnosticReportRequest, request: Request) -> dict:
    app = request.app.state.odin
    await app.runtime_diagnostics.inspect_runtime_health(mode=body.mode)
    return await app.runtime_diagnostics.generate_runtime_diagnostic_report()


@router.get("/runtime-diagnostics")
async def runtime_diagnostics_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"runtime_diagnostics": app.runtime_diagnostics.snapshot()}


@router.get("/runtime-health")
async def runtime_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_diagnostics.inspect_runtime_health()


@router.post("/resource-optimization/rebalance")
async def resource_optimization_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.resource_optimization.rebalance_render_density()


@router.post("/resource-optimization/low-power")
async def resource_optimization_low_power(request: Request) -> dict:
    app = request.app.state.odin
    return await app.resource_optimization.enter_low_power_coordination()


@router.post("/resource-optimization/compress")
async def resource_optimization_compress(request: Request) -> dict:
    app = request.app.state.odin
    return await app.resource_optimization.compress_runtime_surfaces()


@router.post("/resource-optimization/memory")
async def resource_optimization_memory(request: Request) -> dict:
    app = request.app.state.odin
    return await app.resource_optimization.optimize_memory_pressure()


@router.get("/resource-optimization")
async def resource_optimization_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"resource_optimization": app.resource_optimization.snapshot()}


@router.post("/stream-management/compress")
async def stream_management_compress(request: Request) -> dict:
    app = request.app.state.odin
    return await app.stream_management.compress_stream_channels()


@router.post("/stream-management/prune")
async def stream_management_prune(request: Request) -> dict:
    app = request.app.state.odin
    return await app.stream_management.prune_stale_streams()


@router.get("/stream-management")
async def stream_management_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"stream_management": app.stream_management.snapshot()}


@router.get("/stream-throughput")
async def stream_throughput(request: Request) -> dict:
    app = request.app.state.odin
    return await app.production_observability.measure_stream_throughput()


@router.post("/session-persistence-v2/recover")
async def session_persistence_recover(request: Request) -> dict:
    app = request.app.state.odin
    return await app.session_persistence_v2.recover_interrupted_runtime()


@router.post("/session-persistence-v2/compact")
async def session_persistence_compact(request: Request) -> dict:
    app = request.app.state.odin
    return await app.session_persistence_v2.compact_session_registry()


@router.get("/session-persistence-v2")
async def session_persistence_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"session_persistence_v2": app.session_persistence_v2.snapshot()}


@router.get("/session-persistence")
async def session_persistence_panel(request: Request) -> dict:
    app = request.app.state.odin
    return {"session_persistence_v2": app.session_persistence_v2.snapshot()}


@router.post("/runtime-cleanup/run")
async def runtime_cleanup_run(body: CleanupRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_cleanup.schedule_background_cleanup(mode=body.mode)


@router.get("/runtime-cleanup/status")
async def runtime_cleanup_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"runtime_cleanup": app.runtime_cleanup.snapshot()}


@router.get("/runtime-cleanup")
async def runtime_cleanup_panel(request: Request) -> dict:
    app = request.app.state.odin
    return {"runtime_cleanup": app.runtime_cleanup.snapshot()}


@router.get("/production-observability/metrics")
async def production_observability_metrics(request: Request) -> dict:
    app = request.app.state.odin
    return await app.production_observability.build_runtime_metrics()


@router.get("/production-observability/profile")
async def production_observability_profile(request: Request) -> dict:
    app = request.app.state.odin
    return await app.production_observability.generate_operational_profile()


@router.get("/production-observability")
async def production_observability_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"production_observability": app.production_observability.snapshot()}


@router.get("/runtime-metrics")
async def runtime_metrics(request: Request) -> dict:
    app = request.app.state.odin
    return await app.production_observability.build_runtime_metrics()


@router.get("/startup-profiler")
async def startup_profiler(request: Request) -> dict:
    app = request.app.state.odin
    return await app.production_observability.measure_startup_performance()
