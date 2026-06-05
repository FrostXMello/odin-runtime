"""Safe action engine tests."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from odin_backend.api.routes import action_runtime
from odin_backend.config import Settings
from odin_backend.core.action_safety.destructive_action_detector import is_destructive
from odin_backend.core.action_safety.safety_classifier import ActionSafetyEngine
from odin_backend.core.actions.action_runtime import ActionState
from odin_backend.core.app import OdinApplication
from odin_backend.core.browser_operator.navigation_guard import allow_navigation
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


async def _wait_action(app, action_id: str) -> dict:
    import asyncio

    for _ in range(50):
        entry = app.action_runtime.get(action_id)
        if entry and entry["state"] in (
            ActionState.COMPLETED.value,
            ActionState.FAILED.value,
            ActionState.BLOCKED.value,
            ActionState.REVERTED.value,
        ):
            return entry
        await asyncio.sleep(0.05)
    return app.action_runtime.get(action_id) or {}


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "actions.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        cognitive_learning_enabled=False,
        local_cognition_enabled=True,
        model_provider="mock",
        action_engine_enabled=True,
        desktop_automation_enabled=True,
        browser_operator_enabled=True,
        automation_simulation_mode=True,
        overlay_enabled=True,
        multimodal_perception_enabled=True,
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
async def test_app_has_action_services(app):
    assert hasattr(app, "action_runtime")
    assert hasattr(app, "automation_sandbox")
    assert hasattr(app, "browser_operator")
    assert hasattr(app, "supervision_runtime")
    assert hasattr(app, "macro_replay")
    assert hasattr(app, "action_safety")
    assert hasattr(app, "overlay_runtime")


@pytest.mark.asyncio
async def test_action_lifecycle(app):
    proposed = await app.action_runtime.propose(kind="click", label="Open menu", payload={"x": 10, "y": 20})
    assert proposed["state"] == ActionState.AWAITING_APPROVAL.value
    await app.action_runtime.approve(proposed["id"])
    approved = await _wait_action(app, proposed["id"])
    assert approved["state"] == ActionState.COMPLETED.value
    assert approved["result"]["simulated"] is True


@pytest.mark.asyncio
async def test_approval_gating_blocked_when_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        action_engine_enabled=False,
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    proposed = await odin.action_runtime.propose(kind="click", label="Test", payload={})
    assert proposed["state"] == ActionState.BLOCKED.value
    await odin.shutdown()


@pytest.mark.asyncio
async def test_emergency_stop(app):
    p1 = await app.action_runtime.propose(kind="click", label="A", payload={"x": 1, "y": 1})
    await app.action_runtime.approve(p1["id"])
    result = app.action_runtime.emergency_stop()
    assert result["emergency_stopped"] is True
    p2 = await app.action_runtime.propose(kind="click", label="B", payload={"x": 2, "y": 2})
    approved = await app.action_runtime.approve(p2["id"])
    assert approved["state"] in (ActionState.BLOCKED.value, ActionState.PAUSED.value)


@pytest.mark.asyncio
async def test_workflow_recording(app):
    await app.macro_replay.start_recording()
    action = await app.action_runtime.propose(kind="type_text", label="Type hello", payload={"text": "hi"})
    await app.action_runtime.approve(action["id"])
    stopped = await app.macro_replay.stop_recording(name="test_macro")
    assert stopped["macro"]["name"] == "test_macro"
    macros = await app.workflow_memory.list_macros()
    assert any(m["name"] == "test_macro" for m in macros)


@pytest.mark.asyncio
async def test_rollback_recovery(app):
    action = await app.action_runtime.propose(kind="type_text", label="Type", payload={"text": "abc"})
    await app.action_runtime.approve(action["id"])
    completed = await _wait_action(app, action["id"])
    assert completed["state"] == ActionState.COMPLETED.value
    reverted = await app.action_runtime.revert(action["id"])
    assert reverted["state"] == ActionState.REVERTED.value
    assert reverted["undo"]["reverted"] is True


@pytest.mark.asyncio
async def test_risk_classification_blocked():
    engine = ActionSafetyEngine(None)
    assert engine.classify(kind="delete_file", payload={"path": "/"}, hint=None) == "blocked"
    assert is_destructive("shell_exec", {}) is True


@pytest.mark.asyncio
async def test_browser_navigation_guard():
    ok, _ = allow_navigation("https://example.com")
    assert ok is True
    blocked, reason = allow_navigation("javascript:alert(1)")
    assert blocked is False
    assert "blocked_scheme" in reason


@pytest.mark.asyncio
async def test_browser_supervised_action(app):
    session = await app.browser_operator.start_session()
    assert "id" in session
    proposed = await app.action_runtime.propose(
        kind="navigate", label="Go to docs", payload={"url": "https://example.com"}
    )
    assert proposed["risk"] == "supervised"


@pytest.mark.asyncio
async def test_overlay_state(app):
    action = await app.action_runtime.propose(kind="click", label="Highlight", payload={"x": 50, "y": 60})
    await app.action_runtime.approve(action["id"])
    snap = app.overlay_runtime.snapshot()
    assert snap["enabled"] is True


@pytest.mark.asyncio
async def test_interruption_pause(app):
    proposed = await app.action_runtime.propose(kind="click", label="Pause me", payload={})
    paused = await app.action_runtime.pause(proposed["id"])
    assert paused is not None


@pytest.mark.asyncio
async def test_stream_channels_actions():
    ev = TraceEvent(
        kind=TraceEventKind.ACTION_EXECUTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "actions:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.asyncio
async def test_action_api_routes(app):
    api = FastAPI()
    api.state.odin = app
    api.include_router(action_runtime.router, prefix="/api/v1")
    transport = ASGITransport(app=api)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        assert (await client.get("/api/v1/runtime/actions")).status_code == 200
        r = await client.post(
            "/api/v1/runtime/actions/propose",
            json={"kind": "click", "label": "api test", "payload": {"x": 1, "y": 2}},
        )
        assert r.status_code == 200
        action_id = r.json()["id"]
        assert (await client.post(f"/api/v1/runtime/actions/{action_id}/approve")).status_code == 200
        assert (await client.get("/api/v1/runtime/supervision")).status_code == 200
        assert (await client.post("/api/v1/runtime/emergency-stop")).status_code == 200
        assert (await client.get("/api/v1/runtime/workflows")).status_code == 200
