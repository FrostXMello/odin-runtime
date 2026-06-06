"""Cognitive workstation runtime APIs (Prompt 40)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["cognitive-workstation-runtime"])


class FuseContextRequest(BaseModel):
    ide: dict | None = None
    terminal: dict | None = None
    browser: dict | None = None


class ObserveRequest(BaseModel):
    snapshot: dict = Field(default_factory=dict)


class AssistRequest(BaseModel):
    context: dict = Field(default_factory=dict)
    mode: str | None = None


class WorkflowRequest(BaseModel):
    workflow_id: str
    steps: list[str] = Field(default_factory=list)


class TrackWorkRequest(BaseModel):
    title: str
    project: str


class InferRequest(BaseModel):
    prompt: str
    complexity: float = 0.5
    stream: bool = False


class LearnRequest(BaseModel):
    action: str
    hour: int = 12


@router.get("/workstation")
async def runtime_workstation(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "awareness": app.workstation_awareness.snapshot(),
        "fusion": app.context_fusion.snapshot(),
        "continuity": app.cognitive_continuity.snapshot(),
    }


@router.post("/context/fuse")
async def runtime_context_fuse(body: FuseContextRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.context_fusion.fuse(ide=body.ide, terminal=body.terminal, browser=body.browser)


@router.get("/context")
async def runtime_context(request: Request) -> dict:
    app = request.app.state.odin
    return {"fusion": app.context_fusion.snapshot()}


@router.get("/continuity")
async def runtime_continuity_panel(request: Request) -> dict:
    app = request.app.state.odin
    return {"continuity": app.cognitive_continuity.snapshot()}


@router.post("/continuity/restore")
async def runtime_continuity_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_continuity.restore()


@router.get("/live-cognition")
async def runtime_live_cognition(request: Request) -> dict:
    app = request.app.state.odin
    tick = await app.continuous_cognition.tick()
    return {"continuous": app.continuous_cognition.snapshot(), "last_tick": tick}


@router.post("/live-cognition/tick")
async def runtime_live_cognition_tick(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuous_cognition.tick()


@router.get("/activity-graph")
async def runtime_activity_graph(request: Request) -> dict:
    app = request.app.state.odin
    return {"graph": app.workstation_awareness.snapshot()}


@router.post("/activity-graph/observe")
async def runtime_activity_observe(body: ObserveRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workstation_awareness.observe(snapshot=body.snapshot)


@router.get("/attention")
async def runtime_attention(request: Request) -> dict:
    app = request.app.state.odin
    return {"context": app.context_fusion.snapshot(), "workstation": app.workstation_awareness.snapshot()}


@router.get("/workflow-intelligence")
async def runtime_workflow_intelligence(request: Request) -> dict:
    app = request.app.state.odin
    prediction = await app.workflow_intelligence.predict()
    return {"intelligence": app.workflow_intelligence.snapshot(), "prediction": prediction}


@router.post("/workflow-intelligence/learn")
async def runtime_workflow_learn(body: LearnRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workflow_intelligence.learn(action=body.action, hour=body.hour)


@router.get("/live-copilot")
async def runtime_live_copilot(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_copilot": app.live_copilot.snapshot()}


@router.post("/live-copilot/assist")
async def runtime_live_copilot_assist(body: AssistRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_copilot.assist(context=body.context, mode=body.mode)


@router.post("/execution-coordination/start")
async def runtime_execution_start(body: WorkflowRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_coordination.start_workflow(workflow_id=body.workflow_id, steps=body.steps)


@router.post("/cognitive-pipeline/infer")
async def runtime_cognitive_infer(body: InferRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_pipeline.infer(prompt=body.prompt, complexity=body.complexity, stream=body.stream)


@router.post("/continuity/track")
async def runtime_continuity_track(body: TrackWorkRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_continuity.track_work(title=body.title, project=body.project)
