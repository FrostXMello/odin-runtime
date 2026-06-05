"""Multimodal operator intelligence tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.api.routes import multimodal_runtime
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.desktop.clipboard_memory import ClipboardMemory
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.core.vision.ocr_pipeline import run_ocr


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "multimodal.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        local_cognition_enabled=True,
        model_provider="mock",
        multimodal_perception_enabled=True,
        desktop_awareness_enabled=True,
        voice_enabled=True,
        copilot_mode="suggestion",
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        execution_engine_enabled=True,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_multimodal_services(app):
    assert hasattr(app, "multimodal_perception")
    assert hasattr(app, "desktop_monitor")
    assert hasattr(app, "screen_pipeline")
    assert hasattr(app, "voice_runtime")
    assert hasattr(app, "copilot_runtime")
    assert hasattr(app, "workspace_memory")
    assert hasattr(app, "collaboration_runtime")


@pytest.mark.asyncio
async def test_perception_disabled_by_default(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        multimodal_perception_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    result = await odin.multimodal_perception.update_from_desktop({"active_window": {"app": "test"}})
    assert result["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_perception_state_updates(app):
    snap = await app.desktop_monitor.ingest_snapshot(
        {"active_window": {"app": "Code", "title": "main.py"}, "clipboard": "hello"}
    )
    assert snap["accepted"] is True
    perception = app.multimodal_perception.snapshot()
    assert perception["metrics"]["updates"] >= 1


@pytest.mark.asyncio
async def test_clipboard_privacy_filter():
    mem = ClipboardMemory()
    assert mem.record("my password is secret") is False
    assert mem.record("normal text") is True
    assert len(mem.recent()) == 1


@pytest.mark.asyncio
async def test_ocr_pipeline_stub(app):
    text = await run_ocr(app, "/nonexistent/path.png")
    assert isinstance(text, str)


@pytest.mark.asyncio
async def test_screenshot_capture(app):
    scene = await app.screen_pipeline.capture_and_parse()
    assert "summary" in scene or "ocr_preview" in scene
    assert app.multimodal_perception.snapshot()["metrics"]["snapshots"] >= 1


@pytest.mark.asyncio
async def test_voice_session(app):
    started = await app.voice_runtime.start_session()
    assert started["status"] == "started"
    utterance = await app.voice_runtime.process(text="hello odin")
    assert "response" in utterance
    stopped = await app.voice_runtime.stop_session()
    assert stopped["status"] == "stopped"


@pytest.mark.asyncio
async def test_workspace_pattern_persistence(app):
    await app.desktop_monitor.ingest_snapshot({"active_window": {"app": "Terminal"}})
    patterns = await app.workspace_memory.list_patterns()
    assert any(p["label"] == "Terminal" for p in patterns)


@pytest.mark.asyncio
async def test_copilot_suggestions(app):
    app.copilot_runtime.set_mode("suggestion")
    await app.desktop_monitor.ingest_snapshot(
        {"active_window": {"app": "vscode", "title": "project"}}
    )
    result = await app.copilot_runtime.tick()
    assert result["mode"] == "suggestion"
    assert isinstance(result["suggestions"], list)


@pytest.mark.asyncio
async def test_approval_flow(app):
    entry = await app.collaboration_runtime.request_approval(
        action="run_mission", detail="Execute test suite"
    )
    assert entry["status"] == "pending"
    resolved = await app.collaboration_runtime.resolve_approval(entry["id"], approved=True)
    assert resolved["status"] == "approved"
    snap = app.collaboration_runtime.snapshot()
    assert len(snap["approval_history"]) >= 1


@pytest.mark.asyncio
async def test_multimodal_memory_grounding(app):
    await app.screen_pipeline.capture_and_parse()
    visual = app.multimodal_perception.snapshot()["visual"]
    assert isinstance(visual, list)


@pytest.mark.asyncio
async def test_stream_channels_multimodal():
    ev = TraceEvent(
        kind=TraceEventKind.PERCEPTION_UPDATED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    ch = resolve_channels_for_trace(ev)
    assert "perception:runtime" in ch

    ev2 = TraceEvent(
        kind=TraceEventKind.COPILOT_SUGGESTION_GENERATED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "copilot:runtime" in resolve_channels_for_trace(ev2)


@pytest.mark.asyncio
async def test_multimodal_api_routes(app):
    api = FastAPI()
    api.state.odin = app
    api.include_router(multimodal_runtime.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/api/v1/runtime/perception")).status_code == 200
        assert (await client.get("/api/v1/runtime/desktop")).status_code == 200
        assert (await client.get("/api/v1/runtime/workspace")).status_code == 200
        assert (await client.get("/api/v1/runtime/copilot")).status_code == 200
        assert (await client.get("/api/v1/runtime/collaboration")).status_code == 200
        assert (await client.post("/api/v1/runtime/voice/start")).status_code == 200
        assert (await client.post("/api/v1/runtime/snapshot")).status_code == 200
        assert (await client.get("/api/v1/runtime/screenshots")).status_code == 200
