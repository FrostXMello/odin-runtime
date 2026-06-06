"""Closed-loop predictive recovery APIs (Prompt 61)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["closed-loop-predictive-recovery-runtime"])


class PhaseRequest(BaseModel):
    phase: str = "stabilization"


class VetoRequest(BaseModel):
    path: str = "default"


class ApprovalRequest(BaseModel):
    path: str = "default"
    risk: float = 0.5


@router.post("/predictive-recovery-v2/forecast")
async def predictive_recovery_v2_forecast(request: Request) -> dict:
    app = request.app.state.odin
    return await app.predictive_recovery_v2.forecast_operational_failure()


@router.post("/predictive-recovery-v2/simulate")
async def predictive_recovery_v2_simulate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.predictive_recovery_v2.simulate_recovery_paths()


@router.get("/predictive-recovery-v2")
async def predictive_recovery_v2_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"predictive_recovery_v2": app.predictive_recovery_v2.snapshot()}


@router.post("/recovery-orchestration/initialize")
async def recovery_orchestration_init(request: Request) -> dict:
    app = request.app.state.odin
    return await app.recovery_orchestration.initialize_recovery_cycle()


@router.post("/recovery-orchestration/transition")
async def recovery_orchestration_transition(body: PhaseRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.recovery_orchestration.transition_recovery_phase(phase=body.phase)


@router.get("/recovery-orchestration")
async def recovery_orchestration_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"recovery_orchestration": app.recovery_orchestration.snapshot()}


@router.get("/recovery-phases")
async def recovery_phases(request: Request) -> dict:
    app = request.app.state.odin
    return {"recovery_orchestration": app.recovery_orchestration.snapshot()}


@router.get("/rollback-intelligence/graph")
async def rollback_intelligence_graph(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_intelligence.generate_rollback_graph()


@router.post("/rollback-intelligence/replay")
async def rollback_intelligence_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_intelligence.replay_execution_window()


@router.get("/rollback-intelligence")
async def rollback_intelligence_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"rollback_intelligence": app.rollback_intelligence.snapshot()}


@router.get("/rollback-replay")
async def rollback_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_intelligence.replay_execution_window()


@router.post("/continuity-recovery/restore")
async def continuity_recovery_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuity_recovery.recover_mission_continuity()


@router.get("/continuity-recovery/window")
async def continuity_recovery_window(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuity_recovery.replay_continuity_window()


@router.get("/continuity-recovery")
async def continuity_recovery_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"continuity_recovery": app.continuity_recovery.snapshot()}


@router.post("/stability-loops/rebalance")
async def stability_loops_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.stability_loops.rebalance_runtime_pressure()


@router.post("/stability-loops/throttle")
async def stability_loops_throttle(request: Request) -> dict:
    app = request.app.state.odin
    return await app.stability_loops.throttle_recovery_density()


@router.get("/stability-loops")
async def stability_loops_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"stability_loops": app.stability_loops.snapshot()}


@router.get("/runtime-stability")
async def runtime_stability(request: Request) -> dict:
    app = request.app.state.odin
    return await app.stability_loops.suppress_instability_cascades()


@router.post("/operator-veto/request")
async def operator_veto_request(body: ApprovalRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_veto.request_recovery_approval(path=body.path, risk=body.risk)


@router.post("/operator-veto/authorize")
async def operator_veto_authorize(body: VetoRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_veto.authorize_recovery_chain(path=body.path)


@router.post("/operator-veto/veto")
async def operator_veto_veto(body: VetoRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_veto.veto_recovery_path(path=body.path)


@router.get("/operator-veto")
async def operator_veto_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_veto": app.operator_veto.snapshot()}


@router.get("/recovery-authorization")
async def recovery_authorization(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_veto": app.operator_veto.snapshot()}
