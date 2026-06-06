"""Multi-operator collaborative cognition APIs (Prompt 62)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["multi-operator-collaborative-cognition-runtime"])


class OperatorSessionRequest(BaseModel):
    operator_id: str = "operator-local"
    role: str = "supervisor"


class MissionRequest(BaseModel):
    mission_id: str = "shared-mission"
    operator_id: str = "operator-local"


class DelegationRequest(BaseModel):
    task_id: str = "task-local"
    operator_id: str = "operator-local"


@router.get("/collaborative-cognition/state")
async def collaborative_cognition_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"collaborative_cognition": app.collaborative_cognition.snapshot()}


@router.post("/collaborative-cognition/synchronize")
async def collaborative_cognition_synchronize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.collaborative_cognition.synchronize_operator_state()


@router.post("/collaborative-cognition/initialize")
async def collaborative_cognition_initialize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.collaborative_cognition.initialize_collaboration(profile="team")


@router.post("/operator-sessions/create")
async def operator_sessions_create(body: OperatorSessionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_sessions.create_operator_session(operator_id=body.operator_id, role=body.role)


@router.get("/operator-sessions/active")
async def operator_sessions_active(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_sessions": app.operator_sessions.snapshot()}


@router.get("/operator-sessions/replay")
async def operator_sessions_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_sessions.build_session_replay()


@router.post("/shared-mission-control/create")
async def shared_mission_create(body: MissionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.shared_mission_control.create_shared_mission(
        mission_id=body.mission_id,
        owner=body.operator_id,
    )


@router.post("/shared-mission-control/transfer")
async def shared_mission_transfer(body: MissionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.shared_mission_control.transfer_mission_control(
        mission_id=body.mission_id,
        operator_id=body.operator_id,
    )


@router.get("/shared-mission-control")
async def shared_mission_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"shared_mission_control": app.shared_mission_control.snapshot()}


@router.post("/delegation-engine/delegate")
async def delegation_engine_delegate(body: DelegationRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.delegation_engine.delegate_execution(task_id=body.task_id, operator_id=body.operator_id)


@router.post("/delegation-engine/revoke")
async def delegation_engine_revoke(body: DelegationRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.delegation_engine.revoke_delegation(task_id=body.task_id)


@router.get("/delegation-engine")
async def delegation_engine_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"delegation_engine": app.delegation_engine.snapshot()}


@router.get("/team-coordination/pressure")
async def team_coordination_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.team_coordination.estimate_team_pressure()


@router.post("/team-coordination/rebalance")
async def team_coordination_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.team_coordination.rebalance_team_attention()


@router.get("/team-coordination")
async def team_coordination_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"team_coordination": app.team_coordination.snapshot()}


@router.post("/collaborative-recovery/request")
async def collaborative_recovery_request(body: MissionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.collaborative_recovery.request_team_recovery(mission_id=body.mission_id)


@router.post("/collaborative-recovery/authorize")
async def collaborative_recovery_authorize(body: MissionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.collaborative_recovery.authorize_shared_recovery(mission_id=body.mission_id)


@router.get("/collaborative-recovery")
async def collaborative_recovery_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"collaborative_recovery": app.collaborative_recovery.snapshot()}


@router.get("/shared-command")
async def shared_command(request: Request) -> dict:
    app = request.app.state.odin
    return await app.shared_mission_control.synchronize_mission_state()


@router.get("/operator-presence")
async def operator_presence(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_sessions": app.operator_sessions.snapshot()}


@router.get("/collaboration-replay")
async def collaboration_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_sessions.build_session_replay()
