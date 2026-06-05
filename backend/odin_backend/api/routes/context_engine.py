"""Context engine API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/context-engine", tags=["context-engine"])


class ContextUpdateBody(BaseModel):
    enabled: bool | None = None
    application: str | None = None
    window: str | None = None
    tabs: list[dict[str, str]] | None = None
    terminal_cwd: str | None = None
    terminal_output: str | None = None
    repository: str | None = None
    workflow_id: str | None = None
    conversation_id: str | None = None
    project: str | None = None
    interaction: str | None = None


@router.get("")
async def get_context(request: Request) -> dict:
    app = request.app.state.odin
    session = app.context_engine.get_session()
    return {
        "enabled": app.context_engine.enabled,
        "session": session.model_dump(mode="json") if session else None,
        "explain": app.context_engine.explain_context(),
    }


@router.patch("")
async def update_context(body: ContextUpdateBody, request: Request) -> dict:
    app = request.app.state.odin
    if body.enabled is not None:
        await app.context_engine.set_enabled(body.enabled)
        await app.context.set_enabled(body.enabled)
    session = await app.context_engine.update_environment(
        application=body.application,
        window=body.window,
        tabs=body.tabs,
        terminal_cwd=body.terminal_cwd,
        terminal_output=body.terminal_output,
        repository=body.repository,
        workflow_id=body.workflow_id,
        conversation_id=body.conversation_id,
        project=body.project,
        interaction=body.interaction,
    )
    if session:
        summary = app.desktop_semantics.summarize_current_workspace(session)
        await app.desktop_semantics.emit_analysis(summary)
    return {
        "session": session.model_dump(mode="json") if session else None,
        "summary": app.context_engine.summarize_context_session(),
    }


@router.post("/snapshots")
async def save_snapshot(request: Request, label: str = "manual") -> dict:
    app = request.app.state.odin
    snap = await app.context_engine.save_context_snapshot(label)
    return snap.model_dump(mode="json")


@router.post("/snapshots/{snapshot_id}/restore")
async def restore_snapshot(snapshot_id: str, request: Request) -> dict:
    app = request.app.state.odin
    session = await app.context_engine.restore_context_snapshot(snapshot_id)
    if not session:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return session.model_dump(mode="json")


@router.get("/snapshots")
async def list_snapshots(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [s.model_dump(mode="json") for s in app.context_engine.list_snapshots()]
