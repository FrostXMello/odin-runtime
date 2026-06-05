"""Long-running persistent workflow API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from odin_backend.workflows.persistent import PersistentWorkflow

router = APIRouter(prefix="/persistent-workflows", tags=["persistent-workflows"])


class RegisterPersistentWorkflow(BaseModel):
    name: str
    objective: str
    schedule_cron: str | None = None
    requires_approval: bool = True


@router.get("")
async def list_persistent(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [w.model_dump(mode="json") for w in app.persistent_workflows.list_all()]


@router.post("")
async def register(body: RegisterPersistentWorkflow, request: Request) -> dict:
    app = request.app.state.odin
    w = PersistentWorkflow(
        name=body.name,
        objective=body.objective,
        schedule_cron=body.schedule_cron,
        requires_approval=body.requires_approval,
    )
    app.persistent_workflows.register(w)
    return w.model_dump(mode="json")


@router.post("/{workflow_id}/pause")
async def pause(workflow_id: str, request: Request) -> dict:
    app = request.app.state.odin
    w = await app.persistent_workflows.pause(workflow_id)
    if not w:
        raise HTTPException(status_code=404)
    return w.model_dump(mode="json")


@router.post("/{workflow_id}/resume")
async def resume(workflow_id: str, request: Request) -> dict:
    app = request.app.state.odin
    w = await app.persistent_workflows.resume(workflow_id)
    if not w:
        raise HTTPException(status_code=404)
    return w.model_dump(mode="json")


@router.post("/{workflow_id}/cancel")
async def cancel(workflow_id: str, request: Request) -> dict:
    app = request.app.state.odin
    w = await app.persistent_workflows.cancel(workflow_id)
    if not w:
        raise HTTPException(status_code=404)
    return w.model_dump(mode="json")
