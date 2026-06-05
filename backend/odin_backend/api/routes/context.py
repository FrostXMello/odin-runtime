"""Active context API — opt-in."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/context", tags=["context"])


class ContextUpdate(BaseModel):
    enabled: bool | None = None
    application: str | None = None
    window: str | None = None
    project: str | None = None
    workflow_id: str | None = None


@router.get("")
async def get_context(request: Request) -> dict:
    app = request.app.state.odin
    ctx = await app.context.snapshot()
    return ctx.model_dump(mode="json")


@router.patch("")
async def update_context(body: ContextUpdate, request: Request) -> dict:
    app = request.app.state.odin
    if body.enabled is not None:
        await app.context.set_enabled(body.enabled)
    ctx = await app.context.update(
        application=body.application,
        window=body.window,
        project=body.project,
        workflow_id=body.workflow_id,
    )
    return ctx.model_dump(mode="json")
