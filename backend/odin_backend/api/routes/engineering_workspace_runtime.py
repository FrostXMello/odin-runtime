"""Autonomous engineering workspace APIs (Prompt 39)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["engineering-workspace-runtime"])


class RepoRecordRequest(BaseModel):
    repo: str
    structure: dict = Field(default_factory=dict)


class BugRecordRequest(BaseModel):
    repo: str
    error: str
    fixed: bool = False


class StacktraceRequest(BaseModel):
    stacktrace: str
    repo: str = "local"


class PatchPlanRequest(BaseModel):
    goal: str
    files: list[str] = Field(default_factory=list)


class PatchSandboxRequest(BaseModel):
    diff: str


class GoalRequest(BaseModel):
    title: str
    repo: str


class GraphRequest(BaseModel):
    repo: str
    files: list[str] = Field(default_factory=list)


class AgentTaskRequest(BaseModel):
    task: str


class ValidatePatchRequest(BaseModel):
    before: str
    after: str
    confidence: float = 0.6


class IdeContextRequest(BaseModel):
    snapshot: dict = Field(default_factory=dict)


@router.get("/engineering")
async def runtime_engineering(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "memory": app.engineering_memory.snapshot(),
        "workflows": app.dev_workflows.snapshot(),
        "agents": app.engineering_agents.snapshot(),
    }


@router.post("/engineering/record-repo")
async def runtime_record_repo(body: RepoRecordRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_memory.record_repo(repo=body.repo, structure=body.structure)


@router.post("/engineering/record-bug")
async def runtime_record_bug(body: BugRecordRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_memory.record_bug(repo=body.repo, error=body.error, fixed=body.fixed)


@router.post("/debugging/analyze")
async def runtime_debugging_analyze(body: StacktraceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_debugging.analyze(stacktrace=body.stacktrace, repo=body.repo)


@router.get("/patches")
async def runtime_patches(request: Request) -> dict:
    app = request.app.state.odin
    return {"patching": app.patching.snapshot()}


@router.post("/patches/plan")
async def runtime_patches_plan(body: PatchPlanRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.patching.plan(goal=body.goal, files=body.files)


@router.post("/patches/sandbox")
async def runtime_patches_sandbox(body: PatchSandboxRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.patching.sandbox_apply(diff=body.diff)


@router.get("/architecture")
async def runtime_architecture(request: Request) -> dict:
    app = request.app.state.odin
    return {"repository_graph": app.repository_graph.snapshot()}


@router.post("/repository-graph/analyze")
async def runtime_repository_graph(body: GraphRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.repository_graph.analyze(repo=body.repo, files=body.files)


@router.get("/workflows")
async def runtime_workflows(request: Request) -> dict:
    app = request.app.state.odin
    return {"workflows": app.dev_workflows.snapshot()}


@router.post("/workflows/goal")
async def runtime_workflows_goal(body: GoalRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.dev_workflows.create_goal(title=body.title, repo=body.repo)


@router.get("/testing")
async def runtime_testing(request: Request) -> dict:
    app = request.app.state.odin
    return {"validation_fabric": app.validation_fabric.snapshot()}


@router.post("/testing/validate-patch")
async def runtime_testing_validate(body: ValidatePatchRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.validation_fabric.validate_patch(
        before=body.before, after=body.after, confidence=body.confidence
    )


@router.post("/engineering/agents/delegate")
async def runtime_engineering_agents(body: AgentTaskRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_agents.delegate(task=body.task)


@router.post("/developer/ide-context")
async def runtime_ide_context(body: IdeContextRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.integrations_runtime.ingest_ide_context(snapshot=body.snapshot)


@router.get("/engineering/briefing")
async def runtime_engineering_briefing(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_workflow.engineering_briefing()
