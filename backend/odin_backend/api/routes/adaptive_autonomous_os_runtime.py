"""Adaptive autonomous cognitive OS APIs (Prompt 49)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["adaptive-autonomous-os-runtime"])


class ProfileRequest(BaseModel):
    profile: str


class LoadRequest(BaseModel):
    load: float = 0.5


class ProjectRequest(BaseModel):
    project: str = "local"


class GoalRequest(BaseModel):
    goal: str


class PatchRequest(BaseModel):
    patch: str = ""


class ThoughtRequest(BaseModel):
    thought: str


class LowPowerRequest(BaseModel):
    enabled: bool = True


class AnalyzeRequest(BaseModel):
    hours: float = 4.0
    switches: int = 3


class RepoRequest(BaseModel):
    repo: str = "local"


@router.get("/adaptive-runtime")
async def runtime_adaptive_runtime(request: Request) -> dict:
    app = request.app.state.odin
    return {"adaptive_runtime": app.adaptive_runtime.snapshot(), "load_balancer": app.cognitive_load_balancer.snapshot()}


@router.post("/adaptive-runtime/scale")
async def runtime_adaptive_scale(body: LoadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.adaptive_runtime.scale(load=body.load)


@router.post("/adaptive-runtime/optimize")
async def runtime_adaptive_optimize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.adaptive_runtime.optimize_background()


@router.post("/adaptive-runtime/profile")
async def runtime_adaptive_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.adaptive_runtime.set_profile(body.profile)


@router.post("/cognition-load/balance")
async def runtime_cognition_load(body: LoadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_load_balancer.balance(load=body.load)


@router.get("/autonomous-workspace")
async def runtime_autonomous_workspace(request: Request) -> dict:
    app = request.app.state.odin
    return {"autonomous_workspace": app.autonomous_workspace.snapshot()}


@router.post("/autonomous-workspace/open")
async def runtime_autonomous_workspace_open(body: ProjectRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_workspace.open(project=body.project)


@router.post("/session-prediction/next")
async def runtime_session_prediction(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_workspace.predict_next()


@router.post("/workflow-recovery/recover")
async def runtime_workflow_recovery(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_workspace.recover_workflow()


@router.post("/session-restore/daily")
async def runtime_session_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_workspace.daily_resume()


@router.get("/engineering-evolution")
async def runtime_engineering_evolution(request: Request) -> dict:
    app = request.app.state.odin
    return {"engineering_evolution": app.engineering_evolution.snapshot()}


@router.post("/engineering-evolution/analyze")
async def runtime_engineering_evolution_analyze(body: RepoRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution.analyze_repo(repo=body.repo)


@router.post("/engineering-evolution/simulate")
async def runtime_engineering_evolution_simulate(body: PatchRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution.simulate_patch(patch=body.patch)


@router.post("/upgrade-planning/propose")
async def runtime_upgrade_planning(body: GoalRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution.propose_upgrade(goal=body.goal)


@router.get("/operator-intelligence-v2")
async def runtime_operator_intelligence_v2(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_intelligence_v2": app.operator_intelligence_v2.snapshot()}


@router.post("/operator-intelligence-v2/analyze")
async def runtime_operator_intelligence_v2_analyze(body: AnalyzeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v2.analyze(hours=body.hours, switches=body.switches)


@router.post("/cognitive-orchestration/daemon-v2/overnight")
async def runtime_daemon_v2_overnight(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon_v2.overnight()


@router.post("/cognitive-orchestration/daemon-v2/defer")
async def runtime_daemon_v2_defer(body: ThoughtRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon_v2.defer_thought(thought=body.thought)


@router.post("/cognitive-orchestration/daemon-v2/restore")
async def runtime_daemon_v2_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon_v2.restore_deferred()


@router.post("/cognitive-orchestration/daemon-v2/resume")
async def runtime_daemon_v2_resume(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon_v2.resume_cognition()


@router.post("/cognitive-orchestration/daemon-v2/low-power")
async def runtime_daemon_v2_low_power(body: LowPowerRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon_v2.set_low_power(enabled=body.enabled)
