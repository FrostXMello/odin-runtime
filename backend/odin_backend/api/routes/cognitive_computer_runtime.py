"""Persistent cognitive computer APIs (Prompt 48)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["cognitive-computer-runtime"])


class ProfileRequest(BaseModel):
    profile: str


class FocusRequest(BaseModel):
    focus: str


class ContextsRequest(BaseModel):
    contexts: list[dict] = Field(default_factory=list)


class MemoryLinkRequest(BaseModel):
    topic: str
    prior: str = ""


class RecallRequest(BaseModel):
    query: str = ""


class ObserveRequest(BaseModel):
    repo: str = ""
    file: str = ""
    title: str = ""
    app_name: str = ""


class ThoughtRequest(BaseModel):
    thought: str


class ReflectRequest(BaseModel):
    summary: str = "session reflection"


class InteractRequest(BaseModel):
    text: str
    energy: float = 0.6


class AssistanceRequest(BaseModel):
    context: str = ""
    idle_s: float = 0.0
    urgency: float = 0.5


class TickRequest(BaseModel):
    idle_s: float = 0.0


class DeferRequest(BaseModel):
    thought: str


@router.get("/cognitive-kernel")
async def runtime_cognitive_kernel(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_kernel": app.cognitive_kernel.snapshot()}


@router.post("/cognitive-kernel/heartbeat")
async def runtime_cognitive_kernel_heartbeat(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_kernel.heartbeat()


@router.post("/cognitive-kernel/restore")
async def runtime_cognitive_kernel_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_kernel.restore()


@router.post("/cognitive-kernel/focus")
async def runtime_cognitive_kernel_focus(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_kernel.focus(focus=body.focus)


@router.post("/cognitive-kernel/profile")
async def runtime_cognitive_kernel_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_kernel.set_profile(body.profile)


@router.post("/cognitive-kernel/prioritize")
async def runtime_cognitive_kernel_prioritize(body: ContextsRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_kernel.prioritize_context(contexts=body.contexts)


@router.get("/memory-fabric")
async def runtime_memory_fabric(request: Request) -> dict:
    app = request.app.state.odin
    return {"memory_fabric": app.memory_fabric.snapshot()}


@router.post("/memory-fabric/link")
async def runtime_memory_fabric_link(body: MemoryLinkRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric.link(topic=body.topic, prior=body.prior)


@router.post("/memory-fabric/recall")
async def runtime_memory_fabric_recall(body: RecallRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric.recall(query=body.query)


@router.get("/environment-intelligence")
async def runtime_environment_intelligence(request: Request) -> dict:
    app = request.app.state.odin
    return {"environment_intelligence": app.environment_intelligence.snapshot()}


@router.post("/environment-intelligence/observe")
async def runtime_environment_intelligence_observe(body: ObserveRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.environment_intelligence.observe(
        repo=body.repo, file=body.file, title=body.title, app_name=body.app_name
    )


@router.get("/cognitive-streams")
async def runtime_cognitive_streams(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_streams": app.cognitive_streams.snapshot()}


@router.post("/cognitive-streams/push")
async def runtime_cognitive_streams_push(body: ThoughtRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_streams.push(thought=body.thought)


@router.post("/cognitive-streams/reflect")
async def runtime_cognitive_streams_reflect(body: ReflectRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_streams.reflect_stream(summary=body.summary)


@router.post("/cognitive-streams/profile")
async def runtime_cognitive_streams_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_streams.set_profile(body.profile)


@router.get("/personal-presence")
async def runtime_personal_presence(request: Request) -> dict:
    app = request.app.state.odin
    return {"personal_presence": app.personal_presence.snapshot()}


@router.post("/personal-presence/connect")
async def runtime_personal_presence_connect(request: Request) -> dict:
    app = request.app.state.odin
    return await app.personal_presence.connect()


@router.post("/personal-presence/interact")
async def runtime_personal_presence_interact(body: InteractRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.personal_presence.interact(text=body.text, energy=body.energy)


@router.get("/proactive-assistance")
async def runtime_proactive_assistance(request: Request) -> dict:
    app = request.app.state.odin
    return {"proactive_assistance": app.proactive_assistance_runtime.snapshot()}


@router.post("/proactive-assistance/evaluate")
async def runtime_proactive_assistance_evaluate(body: AssistanceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.proactive_assistance_runtime.evaluate(
        context=body.context, idle_s=body.idle_s, urgency=body.urgency
    )


@router.get("/cognitive-orchestration")
async def runtime_cognitive_orchestration(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_orchestration": app.cognitive_orchestration.snapshot()}


@router.post("/cognitive-orchestration/tick")
async def runtime_cognitive_orchestration_tick(body: TickRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_orchestration.cognition_tick(idle_s=body.idle_s)


@router.post("/cognitive-orchestration/overnight")
async def runtime_cognitive_orchestration_overnight(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_orchestration.overnight_cycle()


@router.post("/cognitive-orchestration/defer")
async def runtime_cognitive_orchestration_defer(body: DeferRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_orchestration.defer(thought=body.thought)


@router.post("/cognitive-orchestration/profile")
async def runtime_cognitive_orchestration_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_orchestration.set_profile(body.profile)
