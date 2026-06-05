"""Prompt 35 production runtime — real automation tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.automation.action_verification import click_confidence, verify_action
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
        runtime_guardian_enabled=True,
        self_healing_enabled=True,
        real_automation_enabled=True,
        memory_consolidation_enabled=True,
        survival_mode="balanced",
        automation_mode="simulation",
        automation_simulation_mode=True,
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_automation_runtime(app):
    assert hasattr(app, "automation_runtime")


@pytest.mark.asyncio
async def test_execute_verified_simulation(app):
    r = await app.automation_runtime.execute_verified(
        kind="click",
        payload={"bounds": {"width": 100, "height": 50}},
        expected={"ocr_text": "Submit"},
    )
    assert r["accepted"] is True
    assert r["mode"] == "simulation"
    assert r["verification"]["verified"] is True


@pytest.mark.asyncio
async def test_execute_verified_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        real_automation_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.automation_runtime.execute_verified(kind="click", payload={})
    assert r["accepted"] is False
    assert r["reason"] == "real_automation_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_execute_verified_supervised(app):
    app.settings.automation_mode = "supervised"
    app.settings.automation_simulation_mode = False
    app.automation_runtime._mode = "supervised"
    r = await app.automation_runtime.execute_verified(kind="navigate", payload={"url": "https://example.com"})
    assert r["accepted"] is True
    assert r["mode"] == "supervised"


@pytest.mark.asyncio
async def test_snapshot(app):
    await app.automation_runtime.execute_verified(kind="type", payload={"text": "hello"})
    snap = app.automation_runtime.snapshot()
    assert snap["verifications"] >= 1
    assert snap["mode"] == "simulation"


def test_verify_action_simulation_unit():
    r = verify_action(kind="click", result={"simulated": True, "success": True})
    assert r["verified"] is True
    assert r["score"] == 1.0


def test_verify_action_failure_unit():
    r = verify_action(kind="click", result={"success": False})
    assert r["verified"] is False
    assert "execution_failed" in r["issues"]


def test_verify_action_dom_mismatch_unit():
    r = verify_action(
        kind="click",
        result={"success": True, "dom_hash": "abc", "ocr_text": "wrong"},
        expected={"dom_hash": "xyz", "ocr_text": "expected"},
    )
    assert r["verified"] is False
    assert "dom_mismatch" in r["issues"]


def test_verify_action_ocr_match_unit():
    r = verify_action(
        kind="read",
        result={"success": True, "ocr_text": "hello world"},
        expected={"ocr_text": "world"},
    )
    assert r["verified"] is True


@pytest.mark.parametrize("hit,expected", [(False, 0.0), (True, 0.6)])
def test_click_confidence_no_bounds(hit, expected):
    assert click_confidence(target_bounds=None, hit=hit) == expected


def test_click_confidence_with_bounds():
    conf = click_confidence(target_bounds={"width": 200, "height": 100}, hit=True)
    assert 0.5 < conf <= 1.0


def test_automation_verified_channel():
    ev = TraceEvent(kind=TraceEventKind.AUTOMATION_VERIFIED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "automation:runtime" in resolve_channels_for_trace(ev)


def test_action_retry_generated_channel():
    ev = TraceEvent(kind=TraceEventKind.ACTION_RETRY_GENERATED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "automation:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_execute_verified_bulk(app, i):
    r = await app.automation_runtime.execute_verified(
        kind=f"action-{i % 5}",
        payload={"bounds": {"width": 50 + i, "height": 30}},
    )
    assert r["accepted"] is True
    assert r["result"]["simulated"] is True


@pytest.mark.parametrize("kind", ["click", "type", "scroll", "navigate", "screenshot"])
@pytest.mark.asyncio
async def test_execute_kinds(app, kind):
    r = await app.automation_runtime.execute_verified(kind=kind, payload={"kind": kind})
    assert r["accepted"] is True
    assert r["result"]["kind"] == kind
    assert r["verification"]["verified"] is True


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_verification_count_bulk(app, i):
    await app.automation_runtime.execute_verified(kind="click", payload={"i": i})
    snap = app.automation_runtime.snapshot()
    assert snap["verifications"] >= 1


@pytest.mark.parametrize("width,height", [(10, 10), (100, 50), (500, 300)])
def test_click_confidence_areas(width, height):
    conf = click_confidence(target_bounds={"width": width, "height": height}, hit=True)
    assert 0.0 < conf <= 1.0


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_execute_with_expected_bulk(app, i):
    r = await app.automation_runtime.execute_verified(
        kind="verify",
        payload={"ocr_text": f"text-{i}"},
        expected={"ocr_text": f"text-{i}"},
    )
    assert r["verification"]["verified"] is True


@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_snapshot_recent_bulk(app, i):
    await app.automation_runtime.execute_verified(kind=f"snap-{i}", payload={})
    snap = app.automation_runtime.snapshot()
    assert len(snap["recent"]) >= 1
