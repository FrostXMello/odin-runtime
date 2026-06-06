"""Persistent cognitive environment APIs (Prompt 44)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["persistent-environment-runtime"])


class CheckpointRequest(BaseModel):
    state: dict = Field(default_factory=dict)


class IntentionRequest(BaseModel):
    intention: str


class SummaryRequest(BaseModel):
    summary: str


class UnfinishedRequest(BaseModel):
    title: str
    project: str


class ProjectRequest(BaseModel):
    name: str
    active: bool = True


class ObserveWorkspaceRequest(BaseModel):
    repo: str = ""
    branch: str = "main"
    terminal: dict = Field(default_factory=dict)
    ide: dict = Field(default_factory=dict)
    browser: dict = Field(default_factory=dict)


class ThreadRequest(BaseModel):
    topic: str
    project: str = ""
    thread_id: str = ""


class LinkRequest(BaseModel):
    a: str
    b: str


class EnvironmentRequest(BaseModel):
    duration_s: float = 60.0
    reason: str = ""


class SurfaceRequest(BaseModel):
    mission_id: str = ""
    focus: str = "workspace"
    steps: list[str] = Field(default_factory=list)


@router.get("/persistent-cognition")
async def runtime_persistent_cognition(request: Request) -> dict:
    app = request.app.state.odin
    return {"persistent_cognition": app.persistent_cognition.snapshot()}


@router.post("/persistent-cognition/checkpoint")
async def runtime_persistent_checkpoint(body: CheckpointRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_cognition.checkpoint(state=body.state)


@router.post("/persistent-cognition/rehydrate")
async def runtime_persistent_rehydrate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_cognition.rehydrate_session()


@router.post("/persistent-cognition/defer")
async def runtime_persistent_defer(body: IntentionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_cognition.defer_intention(intention=body.intention)


@router.get("/daily-continuity")
async def runtime_daily_continuity(request: Request) -> dict:
    app = request.app.state.odin
    return {"daily_continuity": app.daily_continuity.snapshot()}


@router.post("/daily-continuity/record")
async def runtime_daily_record(body: SummaryRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_continuity.record_day(summary=body.summary)


@router.post("/daily-continuity/unfinished")
async def runtime_daily_unfinished(body: UnfinishedRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_continuity.track_unfinished(title=body.title, project=body.project)


@router.get("/daily-continuity/resume")
async def runtime_daily_resume(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_continuity.resume_summary()


@router.get("/workspace-presence")
async def runtime_workspace_presence(request: Request) -> dict:
    app = request.app.state.odin
    return {"workspace_presence": app.workspace_presence.snapshot()}


@router.post("/workspace-presence/observe")
async def runtime_workspace_observe(body: ObserveWorkspaceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_presence.observe(
        repo=body.repo, branch=body.branch, terminal=body.terminal, ide=body.ide, browser=body.browser
    )


@router.post("/workspace-presence/restore")
async def runtime_workspace_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_presence.restore_session()


@router.get("/memory-threads")
async def runtime_memory_threads(request: Request) -> dict:
    app = request.app.state.odin
    recall = await app.memory_threads.recall()
    return {"memory_threads": app.memory_threads.snapshot(), "recall": recall}


@router.post("/memory-threads/activate")
async def runtime_memory_threads_activate(body: ThreadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_threads.activate(topic=body.topic, project=body.project, thread_id=body.thread_id)


@router.post("/memory-threads/link")
async def runtime_memory_threads_link(body: LinkRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_threads.link_threads(a=body.a, b=body.b)


@router.get("/live-environment")
async def runtime_live_environment(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_environment": app.live_environment.snapshot()}


@router.post("/live-environment/update")
async def runtime_live_environment_update(body: EnvironmentRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_environment.update(duration_s=body.duration_s, reason=body.reason)


@router.get("/cognitive-surface")
async def runtime_cognitive_surface(request: Request) -> dict:
    app = request.app.state.odin
    render = await app.cognitive_surface.render()
    return {"cognitive_surface": app.cognitive_surface.snapshot(), "render": render}


@router.post("/cognitive-surface/render")
async def runtime_cognitive_surface_render(body: SurfaceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_surface.render(mission_id=body.mission_id, focus=body.focus, steps=body.steps)


@router.get("/project-presence")
async def runtime_project_presence(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "workspace": app.workspace_presence.snapshot(),
        "daily": app.daily_continuity.snapshot(),
    }


@router.post("/project-presence")
async def runtime_project_presence_set(body: ProjectRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_continuity.project(name=body.name, active=body.active)


@router.get("/session-timeline")
async def runtime_session_timeline(request: Request) -> dict:
    app = request.app.state.odin
    return await app.daily_continuity.resume_summary()
