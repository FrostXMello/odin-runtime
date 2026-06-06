"""Cognitive infrastructure APIs (Prompt 51)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["cognitive-infrastructure-runtime"])


class ThoughtRequest(BaseModel):
    thought: str = ""


class LoadRequest(BaseModel):
    load: float = 0.5


class FocusRequest(BaseModel):
    focus: str = "workspace"


class ProjectsRequest(BaseModel):
    projects: list[str] = Field(default_factory=lambda: ["local"])


class ContextRequest(BaseModel):
    context: str = "engineering"


class SessionsRequest(BaseModel):
    sessions: list[str] = Field(default_factory=list)


class RepoRequest(BaseModel):
    repo: str = "local"


class ReposRequest(BaseModel):
    repos: list[str] = Field(default_factory=lambda: ["local"])


class PatchRequest(BaseModel):
    patch: str = ""


class DaysRequest(BaseModel):
    days: int = 30


class ChangeRequest(BaseModel):
    change: str = ""


class LinkRequest(BaseModel):
    a: str
    b: str = ""


class QueryRequest(BaseModel):
    query: str = ""


class TopicRequest(BaseModel):
    topic: str = ""


class CountRequest(BaseModel):
    count: int = 10


class PredictRequest(BaseModel):
    hours: float = 4.0
    switches: int = 3
    context: str = "engineering"


@router.get("/realtime-cognition")
async def runtime_realtime_cognition(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "realtime_cognition": app.realtime_cognition.snapshot(),
        "attention_flow": app.attention_flow.snapshot(),
    }


@router.post("/realtime-cognition/heartbeat")
async def runtime_realtime_heartbeat(request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_cognition.heartbeat()


@router.post("/realtime-cognition/reason")
async def runtime_realtime_reason(body: ThoughtRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_cognition.reason(thought=body.thought)


@router.post("/realtime-cognition/prioritize")
async def runtime_realtime_prioritize(body: LoadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_cognition.prioritize(load=body.load)


@router.post("/attention-flow/route")
async def runtime_attention_flow(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.attention_flow.route(focus=body.focus)


@router.get("/workspace-coordination")
async def runtime_workspace_coordination(request: Request) -> dict:
    app = request.app.state.odin
    return {"workspace_coordination": app.workspace_coordination.snapshot()}


@router.post("/workspace-coordination/coordinate")
async def runtime_workspace_coordinate(body: ProjectsRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_coordination.coordinate(projects=body.projects)


@router.post("/workspace-coordination/predict-restore")
async def runtime_workspace_predict(body: ContextRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_coordination.predict_restore(context=body.context)


@router.post("/multi-project-timeline/unify")
async def runtime_multi_project_timeline(body: SessionsRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_coordination.unify_timeline(sessions=body.sessions)


@router.post("/workspace-coordination/engineering")
async def runtime_workspace_engineering(body: RepoRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_coordination.engineering_session(repo=body.repo)


@router.get("/engineering-infrastructure")
async def runtime_engineering_infrastructure(request: Request) -> dict:
    app = request.app.state.odin
    return {"engineering_infrastructure_v3": app.engineering_infrastructure_v3.snapshot()}


@router.post("/engineering-infrastructure/oversee")
async def runtime_engineering_oversee(body: ReposRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_infrastructure_v3.oversee(repos=body.repos)


@router.post("/engineering-infrastructure/patch-lifecycle")
async def runtime_engineering_patch(body: PatchRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_infrastructure_v3.manage_patch(patch=body.patch)


@router.post("/architecture-forecast/forecast")
async def runtime_architecture_forecast(body: DaysRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_infrastructure_v3.forecast_architecture(days=body.days)


@router.post("/reliability-forecast/forecast")
async def runtime_reliability_forecast(body: ChangeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_infrastructure_v3.forecast_reliability(change=body.change)


@router.get("/memory-intelligence")
async def runtime_memory_intelligence(request: Request) -> dict:
    app = request.app.state.odin
    return {"memory_intelligence": app.memory_intelligence.snapshot()}


@router.post("/memory-intelligence/relate")
async def runtime_memory_relate(body: LinkRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_intelligence.map_relationships(a=body.a, b=body.b)


@router.post("/memory-intelligence/recall")
async def runtime_memory_recall(body: QueryRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_intelligence.recall_contextual(query=body.query)


@router.post("/predictive-memory/resurface")
async def runtime_predictive_memory(body: TopicRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_intelligence.predict_resurface(topic=body.topic)


@router.post("/memory-intelligence/compress")
async def runtime_memory_compress(body: CountRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_intelligence.compress_episodes(count=body.count)


@router.get("/operator-intelligence-v4")
async def runtime_operator_intelligence_v4(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_intelligence_v4": app.operator_intelligence_v4.snapshot()}


@router.post("/operator-intelligence-v4/predict")
async def runtime_operator_predict(body: PredictRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v4.predict(
        hours=body.hours, switches=body.switches, context=body.context
    )


@router.post("/predictive-focus/forecast")
async def runtime_predictive_focus(body: PredictRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v4.forecast_focus(switches=body.switches)


@router.post("/cognitive-load-forecast/forecast")
async def runtime_cognitive_load_forecast(body: PredictRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v4.predict(hours=body.hours, switches=body.switches)


@router.get("/autonomous-activity/radar")
async def runtime_autonomous_activity_radar(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "realtime_cognition": app.realtime_cognition.snapshot(),
        "workspace_coordination": app.workspace_coordination.snapshot(),
        "engineering_infrastructure_v3": app.engineering_infrastructure_v3.snapshot(),
        "memory_intelligence": app.memory_intelligence.snapshot(),
        "bounded": True,
    }


@router.get("/continuous-reasoning")
async def runtime_continuous_reasoning(request: Request) -> dict:
    app = request.app.state.odin
    return {"realtime_cognition": app.realtime_cognition.snapshot(), "continuous": True}
