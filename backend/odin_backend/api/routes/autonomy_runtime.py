"""Autonomous operator mode APIs."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["autonomy-runtime"])


class CreateObjectiveRequest(BaseModel):
    title: str
    description: str = ""
    priority: float = 0.5


class ResearchStartRequest(BaseModel):
    topic: str


class IdentityPatchRequest(BaseModel):
    behavioral: dict | None = None
    communication: dict | None = None


@router.get("/autonomy")
async def runtime_autonomy(request: Request) -> dict:
    app = request.app.state.odin
    return app.autonomous_loop.snapshot()


@router.post("/autonomy/start")
async def runtime_autonomy_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_loop.start()


@router.post("/autonomy/pause")
async def runtime_autonomy_pause(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_loop.pause()


@router.get("/objectives")
async def runtime_objectives(request: Request, status: str | None = None) -> dict:
    app = request.app.state.odin
    objs = await app.objective_manager.list_all(status=status)
    return {"objectives": [o.model_dump(mode="json") for o in objs]}


@router.post("/objectives")
async def runtime_objectives_create(body: CreateObjectiveRequest, request: Request) -> dict:
    app = request.app.state.odin
    obj = await app.objective_manager.create(
        title=body.title, description=body.description, priority=body.priority
    )
    return obj.model_dump(mode="json")


@router.get("/research/debate")
async def runtime_research_debate(request: Request) -> dict:
    app = request.app.state.odin
    return {"sessions": app.research_engine.list_sessions()}


@router.post("/research/debate/start")
async def runtime_research_start(body: ResearchStartRequest, request: Request) -> dict:
    app = request.app.state.odin
    session = await app.research_engine.start(topic=body.topic)
    return session.model_dump(mode="json")


@router.get("/identity")
async def runtime_identity(request: Request) -> dict:
    app = request.app.state.odin
    return app.identity_store.state.model_dump(mode="json")


@router.patch("/identity")
async def runtime_identity_patch(body: IdentityPatchRequest, request: Request) -> dict:
    app = request.app.state.odin
    patch = {}
    if body.behavioral:
        patch["behavioral"] = body.behavioral
    if body.communication:
        patch["communication"] = body.communication
    state = await app.identity_store.update(patch)
    obs = app.observability
    from odin_backend.core.observability.events import TraceEventKind

    obs.tracer.record(
        TraceEventKind.IDENTITY_UPDATED,
        message="identity updated",
        payload={"version": state.version},
        component="identity_store",
    )
    return state.model_dump(mode="json")


@router.get("/environment")
async def runtime_environment(request: Request) -> dict:
    app = request.app.state.odin
    alerts = await app.environment_monitor.collect_alerts()
    return {"alerts": alerts, **app.environment_monitor.snapshot()}


@router.get("/safety")
async def runtime_safety(request: Request) -> dict:
    app = request.app.state.odin
    return app.autonomy_safety.snapshot()
