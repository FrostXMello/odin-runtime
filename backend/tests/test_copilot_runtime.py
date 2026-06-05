"""Prompt 34 production runtime — copilot production tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.copilot.ui_understanding import understand
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace


@pytest.fixture
def settings(tmp_path):
    db = tmp_path / "prod.db"
    return Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        model_provider="mock",
        local_cognition_enabled=True,
        local_ai_enabled=True,
        vector_memory_enabled=True,
        agent_execution_enabled=True,
        agent_society_enabled=True,
        copilot_production_enabled=True,
        realtime_voice_enabled=True,
        evaluation_enabled=True,
        resource_optimization_enabled=True,
        daemon_mode_enabled=True,
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


def _snapshot(app_name: str = "vscode", *, focus: int = 10) -> dict:
    return {
        "app": app_name,
        "title": f"{app_name} — workspace",
        "focus_duration_s": focus,
        "elements": [{"id": "btn-1"}, {"id": "input-1"}],
    }


@pytest.mark.asyncio
async def test_app_has_copilot_production(app):
    assert hasattr(app, "copilot_production")


@pytest.mark.asyncio
async def test_process_snapshot(app):
    r = await app.copilot_production.process_snapshot(_snapshot())
    assert r["accepted"] is True
    assert r["ui"]["app"] == "vscode"
    assert "assistance" in r


@pytest.mark.asyncio
async def test_process_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        copilot_production_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.copilot_production.process_snapshot(_snapshot())
    assert r["accepted"] is False
    await odin.shutdown()


def test_record_action(app):
    app.copilot_production.record_action("open_file")
    app.copilot_production.record_action("run_test")
    snap = app.copilot_production.snapshot()
    assert snap["action_count"] == 2


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.copilot_production.process_snapshot(_snapshot("terminal"))
    app.copilot_production.record_action("ls")
    snap = app.copilot_production.snapshot()
    assert "attention_app" in snap
    assert snap["action_count"] >= 1


def test_copilot_channel():
    ev = TraceEvent(kind=TraceEventKind.COPILOT_SUGGESTION_GENERATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "copilot:runtime" in resolve_channels_for_trace(ev)


def test_proactive_assistance_channel():
    ev = TraceEvent(kind=TraceEventKind.PROACTIVE_ASSISTANCE_TRIGGERED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "copilot:runtime" in resolve_channels_for_trace(ev)


def test_ui_understand_unit():
    ui = understand({"app": "browser", "title": "Docs", "elements": [1, 2, 3]})
    assert ui["app"] == "browser"
    assert ui["elements_detected"] == 3


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_process_bulk(app, i):
    r = await app.copilot_production.process_snapshot(_snapshot(f"app-{i}", focus=i % 60))
    assert r["accepted"] is True


@pytest.mark.parametrize(
    "app_name",
    ["vscode", "terminal", "browser", "slack", "figma", "notion", "xcode", "android-studio", "cursor", "odin"],
)
@pytest.mark.asyncio
async def test_process_apps(app, app_name):
    r = await app.copilot_production.process_snapshot(_snapshot(app_name))
    assert r["ui"]["app"] == app_name


@pytest.mark.parametrize("i", range(15))
def test_record_bulk(app, i):
    app.copilot_production.record_action(f"action-{i}")
    assert app.copilot_production.snapshot()["action_count"] >= 1


@pytest.mark.parametrize("focus", [0, 5, 30, 120, 300])
@pytest.mark.asyncio
async def test_focus_durations(app, focus):
    r = await app.copilot_production.process_snapshot(_snapshot(focus=focus))
    assert r["accepted"] is True
    assert "attention" in r


@pytest.mark.parametrize(
    "action",
    ["save", "build", "deploy", "refactor", "debug", "search", "commit", "review"],
)
def test_record_action_types(app, action):
    app.copilot_production.record_action(action)
    snap = app.copilot_production.snapshot()
    assert snap["action_count"] >= 1
