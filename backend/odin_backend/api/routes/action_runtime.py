"""Safe action engine APIs."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["action-runtime"])


class ProposeActionRequest(BaseModel):
    kind: str
    label: str
    payload: dict = Field(default_factory=dict)
    risk_hint: str | None = None


@router.get("/actions")
async def runtime_actions(request: Request) -> dict:
    app = request.app.state.odin
    return app.action_runtime.snapshot()


@router.post("/actions/propose")
async def runtime_actions_propose(body: ProposeActionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.action_runtime.propose(
        kind=body.kind, label=body.label, payload=body.payload, risk_hint=body.risk_hint
    )


@router.post("/actions/{action_id}/approve")
async def runtime_actions_approve(action_id: str, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.action_runtime.approve(action_id)
    if not result:
        return {"error": "action not found or not approvable", "id": action_id}
    return result


@router.post("/actions/{action_id}/pause")
async def runtime_actions_pause(action_id: str, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.action_runtime.pause(action_id)
    if not result:
        return {"error": "action not found", "id": action_id}
    return result


@router.post("/actions/{action_id}/cancel")
async def runtime_actions_cancel(action_id: str, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.action_runtime.cancel(action_id)
    if not result:
        return {"error": "action not found", "id": action_id}
    return result


@router.post("/actions/{action_id}/revert")
async def runtime_actions_revert(action_id: str, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.action_runtime.revert(action_id)
    if not result:
        return {"error": "action not revertible", "id": action_id}
    return result


@router.get("/workflows")
async def runtime_workflows(request: Request) -> dict:
    app = request.app.state.odin
    macros = await app.workflow_memory.list_macros()
    return {"macros": macros, "recorder": app.macro_replay.snapshot()}


@router.post("/workflows/record/start")
async def runtime_workflows_record_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.macro_replay.start_recording()


@router.post("/workflows/record/stop")
async def runtime_workflows_record_stop(request: Request, name: str = "recorded_workflow") -> dict:
    app = request.app.state.odin
    return await app.macro_replay.stop_recording(name=name)


@router.get("/browser")
async def runtime_browser_operator(request: Request) -> dict:
    app = request.app.state.odin
    return app.browser_operator.snapshot()


@router.post("/browser/session/start")
async def runtime_browser_session_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.browser_operator.start_session()


@router.get("/supervision")
async def runtime_supervision(request: Request) -> dict:
    app = request.app.state.odin
    return app.supervision_runtime.snapshot()


@router.post("/emergency-stop")
async def runtime_emergency_stop(request: Request) -> dict:
    app = request.app.state.odin
    result = app.action_runtime.emergency_stop()
    app.supervision_runtime._interventions.record(kind="emergency_stop")
    return result


@router.get("/automation")
async def runtime_automation(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "simulation_mode": app.settings.automation_simulation_mode,
        "desktop_automation_enabled": app.settings.desktop_automation_enabled,
        "overlay": app.overlay_runtime.snapshot(),
    }


@router.get("/overlay")
async def runtime_overlay(request: Request) -> dict:
    app = request.app.state.odin
    return app.overlay_runtime.snapshot()
