"""Adaptive runtime diagnostics API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/runtime", tags=["adaptive-runtime"])


@router.get("/confidence")
async def runtime_confidence(request: Request) -> dict:
    app = request.app.state.odin
    snap = app.confidence.global_snapshot
    global_data = snap.model_dump()
    global_data["aggregate"] = snap.aggregate
    missions = {}
    for mid in list(app.mission_manager._active.keys())[:10]:  # noqa: SLF001
        ms = app.confidence.for_mission(mid)
        md = ms.model_dump()
        md["aggregate"] = ms.aggregate
        missions[mid] = md
    return {"global": global_data, "aggregate": snap.aggregate, "missions": missions}


@router.get("/adaptive-state")
async def runtime_adaptive_state(request: Request) -> dict:
    app = request.app.state.odin
    return app.mission_execution_adaptive.snapshot(app)


@router.get("/environment")
async def runtime_environment(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "awareness": app.perception.environment_awareness(app),
        "adaptive_policy": app.adaptive_policy.state.model_dump(),
        "runtime_observers_enabled": app.settings.runtime_observers_enabled,
    }
