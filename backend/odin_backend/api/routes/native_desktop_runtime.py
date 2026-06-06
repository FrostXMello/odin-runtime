"""Native cognitive desktop APIs (Prompt 43)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["native-desktop-runtime"])


class WorkspaceRequest(BaseModel):
    workspace: dict = Field(default_factory=dict)


class CommandRequest(BaseModel):
    query: str
    workspace: dict = Field(default_factory=dict)


class QuickActionRequest(BaseModel):
    action: str


class NotifyRequest(BaseModel):
    title: str
    body: str


class ModeRequest(BaseModel):
    mode: str


class RenderRequest(BaseModel):
    thinking: bool = False
    idle: bool = False


class InteractRequest(BaseModel):
    text: str
    workspace: dict = Field(default_factory=dict)
    thread_id: str = ""
    voice: bool = False


class RestoreThreadRequest(BaseModel):
    thread_id: str


class StreamRequest(BaseModel):
    thought: str
    steps: list[str] = Field(default_factory=list)


class EngineeringRequest(BaseModel):
    repo: str
    terminal: dict = Field(default_factory=dict)
    ide: dict = Field(default_factory=dict)
    error: str = ""


class DaemonTickRequest(BaseModel):
    wakeword: str = ""
    energy: float = 0.0


class DeferRequest(BaseModel):
    thought: str


class InterruptRequest(BaseModel):
    reason: str = "operator"


class FamiliarityRequest(BaseModel):
    familiarity: float = 0.5


@router.get("/native-shell")
async def runtime_native_shell(request: Request) -> dict:
    app = request.app.state.odin
    return {"shell": app.native_shell.snapshot(), "immersive": app.immersive_ui.snapshot()}


@router.post("/native-shell/activate")
async def runtime_native_shell_activate(body: WorkspaceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_shell.activate(workspace=body.workspace)


@router.post("/native-shell/command")
async def runtime_native_shell_command(body: CommandRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_shell.command(query=body.query, workspace=body.workspace)


@router.post("/native-shell/quick-action")
async def runtime_native_shell_quick(body: QuickActionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_shell.quick_action(action=body.action)


@router.post("/native-shell/notify")
async def runtime_native_shell_notify(body: NotifyRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_shell.notify(title=body.title, body=body.body)


@router.get("/immersive")
async def runtime_immersive(request: Request) -> dict:
    app = request.app.state.odin
    render = await app.immersive_ui.render()
    return {"immersive": app.immersive_ui.snapshot(), "render": render}


@router.post("/immersive/mode")
async def runtime_immersive_mode(body: ModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.immersive_ui.set_mode(body.mode)


@router.post("/immersive/render")
async def runtime_immersive_render(body: RenderRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.immersive_ui.render(thinking=body.thinking, idle=body.idle)


@router.get("/conversational-os")
async def runtime_conversational_os(request: Request) -> dict:
    app = request.app.state.odin
    return {"conversational_os": app.conversational_os.snapshot()}


@router.post("/conversational-os")
async def runtime_conversational_os_interact(body: InteractRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversational_os.interact(
        text=body.text, workspace=body.workspace, thread_id=body.thread_id, voice=body.voice
    )


@router.post("/conversational-os/restore")
async def runtime_conversational_os_restore(body: RestoreThreadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversational_os.restore(thread_id=body.thread_id)


@router.get("/reasoning-streams")
async def runtime_reasoning_streams(request: Request) -> dict:
    app = request.app.state.odin
    return {"streams": app.reasoning_streams.snapshot()}


@router.post("/reasoning-streams/push")
async def runtime_reasoning_streams_push(body: StreamRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.reasoning_streams.push(thought=body.thought, steps=body.steps)


@router.get("/live-engineering")
async def runtime_live_engineering(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_engineering": app.live_engineering.snapshot()}


@router.post("/live-engineering/session")
async def runtime_live_engineering_session(body: EngineeringRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_engineering.session(
        repo=body.repo, terminal=body.terminal, ide=body.ide, error=body.error
    )


@router.get("/presence-live")
async def runtime_presence_live(request: Request) -> dict:
    app = request.app.state.odin
    pres = await app.presence.update(idle_s=0)
    refined = await app.presence.refine_style(familiarity=0.6)
    return {"presence": pres, "style": refined, "native": app.native_shell.snapshot()}


@router.post("/presence-live/refine")
async def runtime_presence_refine(body: FamiliarityRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.presence.refine_style(familiarity=body.familiarity)


@router.get("/cognitive-daemon")
async def runtime_cognitive_daemon(request: Request) -> dict:
    app = request.app.state.odin
    return {"daemon": app.daemon_runtime.snapshot()}


@router.post("/cognitive-daemon/tick")
async def runtime_cognitive_daemon_tick(body: DaemonTickRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.cognitive_tick(wakeword=body.wakeword, energy=body.energy)


@router.post("/cognitive-daemon/defer")
async def runtime_cognitive_daemon_defer(body: DeferRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.defer_reasoning(thought=body.thought)


@router.post("/cognitive-daemon/interrupt")
async def runtime_cognitive_daemon_interrupt(body: InterruptRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daemon_runtime.handle_interrupt(reason=body.reason)
