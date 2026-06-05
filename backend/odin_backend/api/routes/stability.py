"""Cognitive stability API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from odin_backend.core.autonomy.layer import AutonomyLevel

router = APIRouter(prefix="/stability", tags=["stability"])


class AutonomyLevelBody(BaseModel):
    level: int


@router.get("/coherence")
async def get_coherence(request: Request) -> dict:
    app = request.app.state.odin
    return app.coherence.last_report.model_dump()


@router.post("/coherence/validate")
async def validate_coherence(request: Request) -> dict:
    app = request.app.state.odin
    state = app.kernel.get_state()
    report = app.coherence.validate(state, app.kernel.recent_signals(30))
    return report.model_dump()


@router.get("/snapshots")
async def list_snapshots(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [s.model_dump(mode="json") for s in app.snapshots.list_snapshots()]


@router.post("/snapshots")
async def create_snapshot(request: Request, label: str = "manual") -> dict:
    app = request.app.state.odin
    snap = app.snapshots.create_snapshot(app, label=label)
    return snap.model_dump(mode="json")


@router.get("/snapshots/{snapshot_id}/diff/{other_id}")
async def diff_snapshots(snapshot_id: str, other_id: str, request: Request) -> dict:
    app = request.app.state.odin
    return app.snapshots.diff_snapshots(snapshot_id, other_id)


@router.post("/stability-loop")
async def run_stability_loop(request: Request) -> dict:
    app = request.app.state.odin
    return await app.stability.run_cycle(app)


@router.get("/stability-loop/last")
async def last_stability_audit(request: Request) -> dict:
    app = request.app.state.odin
    return app.stability.last_audit()


@router.post("/memory/refine")
async def refine_memory(request: Request) -> dict:
    app = request.app.state.odin
    report = await app.memory_refinement.refine()
    return report.model_dump()


@router.get("/autonomy")
async def get_autonomy(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "level": app.autonomy.current_level,
        "description": AutonomyLevel(app.autonomy.current_level).name,
    }


@router.patch("/autonomy")
async def set_autonomy(body: AutonomyLevelBody, request: Request) -> dict:
    app = request.app.state.odin
    if body.level < 0 or body.level > 4:
        raise HTTPException(status_code=400, detail="Level must be 0-4")
    app.autonomy.set_level(body.level)
    return {"level": app.autonomy.current_level}
