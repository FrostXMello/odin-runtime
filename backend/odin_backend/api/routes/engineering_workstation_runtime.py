"""Autonomous engineering workstation APIs (Prompt 47)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["engineering-workstation-runtime"])


class ObserveRequest(BaseModel):
    repo: str = "local"
    file: str = ""
    error: str = ""
    logs: list[str] = Field(default_factory=list)


class ProfileRequest(BaseModel):
    profile: str


class AnalyzeRequest(BaseModel):
    stacktrace: str
    repo: str = "local"


class TestsRequest(BaseModel):
    tests: list[str] = Field(default_factory=list)


class GoalRequest(BaseModel):
    goal: str
    repo: str = "local"


class ExperimentRequest(BaseModel):
    name: str
    proposal: dict = Field(default_factory=dict)


class RememberRequest(BaseModel):
    repo: str
    decision: str = ""
    issue: str = ""


class ResumeRequest(BaseModel):
    repo: str = ""


class CouncilRequest(BaseModel):
    topic: str
    patch: str = ""


class TickRequest(BaseModel):
    repo: str = "local"
    idle_s: float = 0.0


class OvernightRequest(BaseModel):
    repo: str = "local"


class RollbackRequest(BaseModel):
    target: str = "last_stable"


@router.get("/live-engineering")
async def runtime_live_engineering(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_engineering_orchestrator": app.live_engineering_orchestrator.snapshot()}


@router.post("/live-engineering/observe")
async def runtime_live_engineering_observe(body: ObserveRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_engineering_orchestrator.observe(
        repo=body.repo, file=body.file, error=body.error, logs=body.logs
    )


@router.post("/live-engineering/restore")
async def runtime_live_engineering_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_engineering_orchestrator.restore()


@router.post("/live-engineering/profile")
async def runtime_live_engineering_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_engineering_orchestrator.set_profile(body.profile)


@router.post("/autonomous-debugging/analyze")
async def runtime_autonomous_debugging_analyze(body: AnalyzeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_debugging_pipeline.analyze(stacktrace=body.stacktrace, repo=body.repo)


@router.post("/autonomous-debugging/map-tests")
async def runtime_autonomous_debugging_map(body: TestsRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_debugging_pipeline.map_tests(tests=body.tests)


@router.get("/engineering-workflows")
async def runtime_engineering_workflows(request: Request) -> dict:
    app = request.app.state.odin
    return {"engineering_workflows_v2": app.engineering_workflows_v2.snapshot()}


@router.post("/engineering-workflows/plan")
async def runtime_engineering_workflows_plan(body: GoalRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_workflows_v2.plan(goal=body.goal, repo=body.repo)


@router.post("/engineering-workflows/advance")
async def runtime_engineering_workflows_advance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_workflows_v2.advance_stage()


@router.get("/engineering-workflows/resume")
async def runtime_engineering_workflows_resume(request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_workflows_v2.resume()


@router.get("/self-improvement-sandbox")
async def runtime_sandbox(request: Request) -> dict:
    app = request.app.state.odin
    return {"self_improvement_sandbox": app.self_improvement_sandbox.snapshot()}


@router.post("/self-improvement-sandbox/experiment")
async def runtime_sandbox_experiment(body: ExperimentRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_improvement_sandbox.experiment(name=body.name, proposal=body.proposal)


@router.post("/self-improvement-sandbox/rollback-rehearsal")
async def runtime_sandbox_rollback(body: RollbackRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_improvement_sandbox.rollback_rehearsal(target=body.target)


@router.get("/project-memory")
async def runtime_project_memory(request: Request) -> dict:
    app = request.app.state.odin
    return {"project_memory": app.project_memory.snapshot()}


@router.post("/project-memory/remember")
async def runtime_project_memory_remember(body: RememberRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.project_memory.remember(repo=body.repo, decision=body.decision, issue=body.issue)


@router.post("/project-memory/resume")
async def runtime_project_memory_resume(body: ResumeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.project_memory.resume(repo=body.repo)


@router.get("/engineering-society")
async def runtime_engineering_society(request: Request) -> dict:
    app = request.app.state.odin
    return {"engineering_society": app.engineering_society.snapshot()}


@router.post("/engineering-society/convene")
async def runtime_engineering_society_convene(body: CouncilRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_society.convene(topic=body.topic, patch=body.patch)


@router.get("/continuous-engineering")
async def runtime_continuous_engineering(request: Request) -> dict:
    app = request.app.state.odin
    return {"continuous_engineering": app.continuous_engineering.snapshot()}


@router.post("/continuous-engineering/tick")
async def runtime_continuous_engineering_tick(body: TickRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuous_engineering.engineering_tick(repo=body.repo, idle_s=body.idle_s)


@router.post("/continuous-engineering/overnight")
async def runtime_continuous_engineering_overnight(body: OvernightRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuous_engineering.overnight(repo=body.repo)


@router.post("/continuous-engineering/profile")
async def runtime_continuous_engineering_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuous_engineering.set_profile(body.profile)
