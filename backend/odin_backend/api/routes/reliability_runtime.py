"""Reliability runtime APIs (Prompt 35)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["reliability-runtime"])


class AutomationExecuteRequest(BaseModel):
    kind: str
    payload: dict = Field(default_factory=dict)
    expected: dict = Field(default_factory=dict)


class HealRequest(BaseModel):
    mission_id: str | None = None


class SurvivalRequest(BaseModel):
    mode: str | None = None


@router.get("/stability")
async def runtime_stability(request: Request) -> dict:
    app = request.app.state.odin
    return {"stability": app.runtime_guardian.snapshot()}


@router.post("/stability/supervise")
async def runtime_stability_supervise(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_guardian.supervise()


@router.post("/stability/recover")
async def runtime_stability_recover(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_guardian.recover()


@router.post("/stability/emergency")
async def runtime_stability_emergency(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_guardian.emergency()


@router.get("/self-healing")
async def runtime_self_healing(request: Request) -> dict:
    app = request.app.state.odin
    return {"self_healing": app.self_healing.snapshot()}


@router.post("/self-healing/heal")
async def runtime_self_healing_heal(body: HealRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_healing.heal(mission_id=body.mission_id)


@router.get("/automation-live")
async def runtime_automation_live(request: Request) -> dict:
    app = request.app.state.odin
    return {"automation": app.automation_runtime.snapshot()}


@router.post("/automation-live/execute")
async def runtime_automation_execute(body: AutomationExecuteRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.automation_runtime.execute_verified(
        kind=body.kind, payload=body.payload, expected=body.expected
    )


@router.post("/vector-memory/consolidate")
async def runtime_memory_consolidate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.vector_memory.consolidate()


@router.post("/resource-optimization/survive")
async def runtime_resource_survive(body: SurvivalRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.resource_optimization.survive(mode=body.mode)


@router.post("/daemon/restore")
async def runtime_daemon_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.restore_session()


@router.post("/copilot/restore-workspace")
async def runtime_copilot_restore_workspace(request: Request) -> dict:
    app = request.app.state.odin
    return await app.copilot_production.restore_workspace()
