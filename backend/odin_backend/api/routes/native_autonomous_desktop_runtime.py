"""Native autonomous desktop APIs (Prompt 54)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["native-autonomous-desktop-runtime"])


class NotifyRequest(BaseModel):
    title: str
    body: str = ""


class LowPowerRequest(BaseModel):
    enabled: bool = True


class WindowRequest(BaseModel):
    window: str = "Odin"
    app: str = ""


class OverlayRequest(BaseModel):
    overlay_type: str


class ContextRequest(BaseModel):
    context: str = ""


class SessionRequest(BaseModel):
    session_id: str = "default"
    repo: str = ""
    files: list[str] = Field(default_factory=list)


class FocusRequest(BaseModel):
    minutes: int = 45


class WorkspaceRequest(BaseModel):
    workspace: str = "engineering"


@router.get("/native-desktop/status")
async def native_desktop_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"native_desktop": app.native_desktop.snapshot()}


@router.post("/native-desktop/initialize")
async def native_desktop_initialize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_desktop.initialize_desktop_runtime()


@router.post("/native-desktop/restore")
async def native_desktop_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_desktop.restore_desktop_session()


@router.post("/native-desktop/notify")
async def native_desktop_notify(body: NotifyRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_desktop.dispatch_native_notification(title=body.title, body=body.body)


@router.post("/native-desktop/low-power")
async def native_desktop_low_power(body: LowPowerRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_desktop.enter_low_power_mode(enabled=body.enabled)


@router.get("/window-awareness/active")
async def window_awareness_active(request: Request) -> dict:
    app = request.app.state.odin
    return {"window_awareness": app.window_awareness.snapshot()}


@router.get("/window-awareness/workspace")
async def window_awareness_workspace(request: Request) -> dict:
    app = request.app.state.odin
    return await app.window_awareness.build_workspace_snapshot()


@router.post("/window-awareness/transition")
async def window_awareness_transition(body: WindowRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.window_awareness.detect_workspace_transition(window=body.window, app=body.app)


@router.post("/window-awareness/classify")
async def window_awareness_classify(request: Request) -> dict:
    app = request.app.state.odin
    return await app.window_awareness.classify_active_window()


@router.get("/live-overlays-v2")
async def live_overlays_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_overlays_v2": app.live_overlays_v2.snapshot()}


@router.post("/live-overlays-v2/attach")
async def live_overlays_attach(body: OverlayRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_overlays_v2.attach_overlay(overlay_type=body.overlay_type)


@router.post("/live-overlays-v2/suppress")
async def live_overlays_suppress(body: OverlayRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_overlays_v2.suppress_overlay(overlay_type=body.overlay_type)


@router.post("/live-overlays-v2/context")
async def live_overlays_context(body: ContextRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_overlays_v2.update_overlay_context(context=body.context)


@router.get("/workspace-sessions")
async def workspace_sessions_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"workspace_sessions": app.workspace_sessions.snapshot()}


@router.post("/workspace-sessions/save")
async def workspace_sessions_save(body: SessionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_sessions.save_workspace_session(
        session_id=body.session_id, repo=body.repo, files=body.files
    )


@router.post("/workspace-sessions/restore")
async def workspace_sessions_restore(body: SessionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_sessions.restore_workspace_session(session_id=body.session_id)


@router.get("/resume-chain")
async def resume_chain(request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_sessions.build_resume_chain()


@router.get("/operator-focus/state")
async def operator_focus_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_focus": app.operator_focus.snapshot()}


@router.post("/operator-focus/start")
async def operator_focus_start(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_focus.start_focus_session(minutes=body.minutes)


@router.get("/operator-focus/pressure")
async def operator_focus_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_focus.estimate_distraction_pressure()


@router.get("/focus-recovery")
async def focus_recovery(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_focus.recommend_focus_recovery()


@router.get("/desktop-attention")
async def desktop_attention(request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_attention.prioritize_desktop_attention()


@router.post("/desktop-attention/salience")
async def desktop_attention_salience(body: WorkspaceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_attention.compute_workspace_salience(workspace=body.workspace)


@router.get("/workspace-transitions")
async def workspace_transitions(request: Request) -> dict:
    app = request.app.state.odin
    return await app.window_awareness.build_workspace_snapshot()


@router.get("/overlay-center")
async def overlay_center(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_overlays_v2": app.live_overlays_v2.snapshot(), "desktop_attention": app.desktop_attention.snapshot()}
