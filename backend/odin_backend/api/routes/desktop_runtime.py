"""Desktop runtime ingestion API."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/desktop-runtime", tags=["desktop-runtime"])


class DesktopSnapshotIn(BaseModel):
    active_app: str | None = None
    active_window: dict | None = None
    project: str = "PROJECT_ODIN"
    vscode: dict | None = None
    browser_tabs: list[dict[str, str]] | None = None
    terminals: list[dict[str, str]] | None = None
    clipboard_preview: str | None = None
    monitors: int | None = None
    platform: str | None = None
    collector: str = "api_ingest"


class CollectorToggle(BaseModel):
    enabled: bool


@router.get("")
async def get_runtime_state(request: Request) -> dict:
    app = request.app.state.odin
    return app.desktop_runtime.get_state()


@router.patch("")
async def toggle_collector(body: CollectorToggle, request: Request) -> dict:
    app = request.app.state.odin
    await app.desktop_runtime.set_enabled(body.enabled)
    return app.desktop_runtime.get_state()


@router.post("/ingest")
async def ingest_snapshot(body: DesktopSnapshotIn, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.desktop_runtime.ingest_snapshot(
        body.model_dump(exclude_none=True),
        collector=body.collector,
    )
    if result.get("accepted"):
        ctx = app.context_engine.get_session()
        ws = app.workspace_intelligence.summarize_workspace(ctx)
        await app.workspace_intelligence.emit_summary(ws)
        if ctx and ctx.insight:
            await app.live_cognition.ingest_context_shift(ctx.insight)
    return result
