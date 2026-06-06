"""Cognitive interface + embodied presence APIs (Prompt 41)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["cognitive-interface-runtime"])


class ActivateShellRequest(BaseModel):
    workspace: dict = Field(default_factory=dict)


class ChatRequest(BaseModel):
    prompt: str
    mode: str | None = None
    context: dict = Field(default_factory=dict)
    thread_id: str = ""


class RestoreThreadRequest(BaseModel):
    thread_id: str


class PresenceUpdateRequest(BaseModel):
    energy: float | None = None
    idle_s: float = 0.0


class RenderVisualizationRequest(BaseModel):
    thought: str = ""
    steps: list[str] = Field(default_factory=list)


class OverlayRequest(BaseModel):
    context: dict = Field(default_factory=dict)
    mode: str | None = None


class SelfDevAnalyzeRequest(BaseModel):
    metrics: dict = Field(default_factory=dict)


class SelfDevProposeRequest(BaseModel):
    title: str
    plan: list[str] = Field(default_factory=list)


class ExplainRequest(BaseModel):
    feature: str
    confidence: float = 0.7
    reason: str = ""


class UiModeRequest(BaseModel):
    mode: str


@router.get("/presence")
async def runtime_presence(request: Request) -> dict:
    app = request.app.state.odin
    return {"presence": app.presence.snapshot(), "shell": app.cognitive_shell.snapshot()}


@router.post("/presence/update")
async def runtime_presence_update(body: PresenceUpdateRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.presence.update(energy=body.energy, idle_s=body.idle_s)


@router.get("/cognition-live")
async def runtime_cognition_live(request: Request) -> dict:
    app = request.app.state.odin
    viz = await app.cognitive_visualization.render(thought="active cognition")
    return {
        "visualization": app.cognitive_visualization.snapshot(),
        "shell": app.cognitive_shell.snapshot(),
        "last_render": viz,
    }


@router.get("/thought-stream")
async def runtime_thought_stream(request: Request) -> dict:
    app = request.app.state.odin
    return {"stream": app.cognitive_visualization.snapshot()}


@router.post("/thought-stream/push")
async def runtime_thought_push(body: RenderVisualizationRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_visualization.render(thought=body.thought, steps=body.steps)


@router.get("/live-overlay")
async def runtime_live_overlay_panel(request: Request) -> dict:
    app = request.app.state.odin
    return {"overlay": app.live_overlay.snapshot()}


@router.post("/live-overlay")
async def runtime_live_overlay_render(body: OverlayRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_overlay.render(context=body.context, mode=body.mode)


@router.get("/conversation")
async def runtime_conversation(request: Request) -> dict:
    app = request.app.state.odin
    return {"conversation": app.conversation.snapshot()}


@router.post("/conversation")
async def runtime_conversation_chat(body: ChatRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversation.chat(
        prompt=body.prompt,
        mode=body.mode,
        context=body.context,
        thread_id=body.thread_id,
    )


@router.post("/conversation/restore")
async def runtime_conversation_restore(body: RestoreThreadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversation.restore_thread(thread_id=body.thread_id)


@router.get("/personality")
async def runtime_personality(request: Request) -> dict:
    app = request.app.state.odin
    pres = await app.presence.update(idle_s=0)
    return {"personality": pres.get("personality"), "presence": app.presence.snapshot()}


@router.get("/self-development")
async def runtime_self_development(request: Request) -> dict:
    app = request.app.state.odin
    return {"self_development": app.self_development.snapshot()}


@router.post("/self-development/analyze")
async def runtime_self_development_analyze(body: SelfDevAnalyzeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_development.analyze(metrics=body.metrics or None)


@router.post("/self-development/propose")
async def runtime_self_development_propose(body: SelfDevProposeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_development.propose(title=body.title, plan=body.plan)


@router.get("/reasoning-map")
async def runtime_reasoning_map(request: Request) -> dict:
    app = request.app.state.odin
    render = await app.cognitive_visualization.render(steps=["observe", "plan", "act", "verify"])
    return {"reasoning_map": render.get("reasoning_map"), "graph": render.get("graph")}


@router.get("/memory-activity")
async def runtime_memory_activity(request: Request) -> dict:
    app = request.app.state.odin
    render = await app.cognitive_visualization.render()
    return {"memory_activity": render.get("memory_activity"), "continuity": app.cognitive_continuity.snapshot()}


@router.post("/cognitive-shell/activate")
async def runtime_shell_activate(body: ActivateShellRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_shell.activate(workspace=body.workspace)


@router.post("/cognitive-shell/ui-mode")
async def runtime_shell_ui_mode(body: UiModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_shell.set_ui_mode(body.mode)


@router.post("/transparency/explain")
async def runtime_transparency_explain(body: ExplainRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.transparency.explain(feature=body.feature, confidence=body.confidence, reason=body.reason)
