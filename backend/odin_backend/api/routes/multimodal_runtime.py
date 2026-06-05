"""Multimodal operator intelligence APIs."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["multimodal-runtime"])


class DesktopSnapshotRequest(BaseModel):
    active_window: dict = Field(default_factory=dict)
    clipboard: str | None = None
    processes: list[dict] = Field(default_factory=list)


class VoiceUtteranceRequest(BaseModel):
    text: str = ""


class ApprovalRequest(BaseModel):
    approved: bool = True
    feedback: str = ""


@router.get("/perception")
async def runtime_perception(request: Request) -> dict:
    app = request.app.state.odin
    return app.multimodal_perception.snapshot()


@router.get("/desktop")
async def runtime_desktop(request: Request) -> dict:
    app = request.app.state.odin
    return app.desktop_monitor.snapshot()


@router.post("/desktop/ingest")
async def runtime_desktop_ingest(body: DesktopSnapshotRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.desktop_monitor.ingest_snapshot(body.model_dump())


@router.get("/workspace")
async def runtime_workspace(request: Request) -> dict:
    app = request.app.state.odin
    patterns = await app.workspace_memory.list_patterns()
    perception = app.multimodal_perception.snapshot()
    return {"patterns": patterns, "workspace": perception.get("workspace", {})}


@router.get("/copilot")
async def runtime_copilot(request: Request) -> dict:
    app = request.app.state.odin
    patterns = await app.workspace_memory.list_patterns()
    return app.copilot_runtime.snapshot(patterns=patterns)


@router.post("/copilot/tick")
async def runtime_copilot_tick(request: Request) -> dict:
    app = request.app.state.odin
    return await app.copilot_runtime.tick()


@router.get("/voice")
async def runtime_voice(request: Request) -> dict:
    app = request.app.state.odin
    return app.voice_runtime.snapshot()


@router.post("/voice/start")
async def runtime_voice_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.voice_runtime.start_session()


@router.post("/voice/stop")
async def runtime_voice_stop(request: Request) -> dict:
    app = request.app.state.odin
    return await app.voice_runtime.stop_session()


@router.post("/voice/utterance")
async def runtime_voice_utterance(body: VoiceUtteranceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.voice_runtime.process(text=body.text)


@router.post("/snapshot")
async def runtime_snapshot(request: Request) -> dict:
    app = request.app.state.odin
    return await app.screen_pipeline.capture_and_parse()


@router.get("/screenshots")
async def runtime_screenshots(request: Request) -> dict:
    app = request.app.state.odin
    return {"paths": app.screen_pipeline.list_screenshots(), "pipeline": app.screen_pipeline.snapshot()}


@router.get("/collaboration")
async def runtime_collaboration(request: Request) -> dict:
    app = request.app.state.odin
    return app.collaboration_runtime.snapshot()


@router.post("/approval/{approval_id}")
async def runtime_approval(approval_id: str, body: ApprovalRequest, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.collaboration_runtime.resolve_approval(
        approval_id, approved=body.approved, feedback=body.feedback
    )
    if not result:
        return {"error": "approval not found", "id": approval_id}
    return result
