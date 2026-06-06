"""Cognitive desktop experience APIs (Prompt 45)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["desktop-experience-runtime"])


class ModeRequest(BaseModel):
    mode: str


class WorkspaceOpenRequest(BaseModel):
    thread_id: str = ""


class InteractRequest(BaseModel):
    text: str
    context: dict = Field(default_factory=dict)


class VisualizationRequest(BaseModel):
    view: str = "reasoning_dag"


class VoiceListenRequest(BaseModel):
    text: str
    energy: float = 0.6
    push_to_talk: bool = False


class FocusRequest(BaseModel):
    focus: str


class OverlayRequest(BaseModel):
    kind: str = "workflow"
    context: dict = Field(default_factory=dict)


@router.get("/desktop-client")
async def runtime_desktop_client(request: Request) -> dict:
    app = request.app.state.odin
    return {"desktop_client": app.desktop_client.snapshot()}


@router.post("/desktop-client/connect")
async def runtime_desktop_client_connect(request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_client.connect()


@router.post("/desktop-client/mode")
async def runtime_desktop_client_mode(body: ModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_client.set_mode(body.mode)


@router.get("/conversation-workspace")
async def runtime_conversation_workspace(request: Request) -> dict:
    app = request.app.state.odin
    return {"conversation_workspace": app.conversation_workspace.snapshot()}


@router.post("/conversation-workspace/open")
async def runtime_conversation_workspace_open(body: WorkspaceOpenRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversation_workspace.open(thread_id=body.thread_id)


@router.post("/conversation-workspace/interact")
async def runtime_conversation_workspace_interact(body: InteractRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversation_workspace.interact(text=body.text, context=body.context)


@router.get("/live-visualization")
async def runtime_live_visualization(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_visualization": app.live_visualization.snapshot()}


@router.post("/live-visualization/render")
async def runtime_live_visualization_render(body: VisualizationRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_visualization.render(view=body.view)


@router.get("/operator-experience")
async def runtime_operator_experience(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_experience": app.daily_operator_experience.snapshot()}


@router.post("/operator-experience/startup")
async def runtime_operator_experience_startup(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_operator_experience.startup()


@router.post("/operator-experience/focus")
async def runtime_operator_experience_focus(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_operator_experience.focus_shift(focus=body.focus)


@router.post("/operator-experience/evolution-review")
async def runtime_operator_experience_evolution(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_operator_experience.evolution_review()


@router.get("/desktop-overlay")
async def runtime_desktop_overlay(request: Request) -> dict:
    app = request.app.state.odin
    return {"desktop_overlay": app.desktop_overlay.snapshot()}


@router.post("/desktop-overlay/attach")
async def runtime_desktop_overlay_attach(body: OverlayRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_overlay.attach(kind=body.kind, context=body.context)


@router.get("/desktop-overlay/memory-surface")
async def runtime_desktop_overlay_memory(request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_overlay.memory_surface()


@router.get("/voice-desktop")
async def runtime_voice_desktop(request: Request) -> dict:
    app = request.app.state.odin
    return {"voice_desktop": app.voice_desktop.snapshot()}


@router.post("/voice-desktop/listen")
async def runtime_voice_desktop_listen(body: VoiceListenRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.voice_desktop.listen(
        text=body.text, energy=body.energy, push_to_talk=body.push_to_talk
    )


@router.post("/voice-desktop/interrupt")
async def runtime_voice_desktop_interrupt(request: Request) -> dict:
    app = request.app.state.odin
    return await app.voice_desktop.interrupt()


@router.post("/voice-desktop/mode")
async def runtime_voice_desktop_mode(body: ModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.voice_desktop.set_mode(body.mode)
