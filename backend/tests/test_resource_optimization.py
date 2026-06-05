"""Prompt 34 production runtime — resource optimization tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.resource_optimization.battery_aware_runtime import throttle_factor
from odin_backend.core.resource_optimization.lightweight_modes import MODES, mode_config
from odin_backend.core.resource_optimization.memory_pressure_runtime import pressure_level
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


@pytest.mark.asyncio
async def test_app_has_resource_optimization(app):
    assert hasattr(app, "resource_optimization")


@pytest.mark.asyncio
async def test_optimize(app):
    r = await app.resource_optimization.optimize()
    assert r["accepted"] is True
    assert "pressure" in r


@pytest.mark.asyncio
async def test_optimize_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        resource_optimization_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.resource_optimization.optimize()
    assert r["accepted"] is False
    await odin.shutdown()


def test_set_mode(app):
    cfg = app.resource_optimization.set_mode("lightweight")
    assert cfg["max_models"] == 1
    assert app.resource_optimization.snapshot()["mode"] == "lightweight"


def test_snapshot(app):
    app.resource_optimization.set_mode("degraded")
    snap = app.resource_optimization.snapshot()
    assert snap["mode"] == "degraded"
    assert "mode_config" in snap


def test_resource_optimized_channel():
    ev = TraceEvent(kind=TraceEventKind.RESOURCE_OPTIMIZED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "resources:runtime" in resolve_channels_for_trace(ev)


def test_mode_config_unit():
    cfg = mode_config("minimal")
    assert cfg["max_models"] == 0


def test_pressure_level_unit():
    r = pressure_level(used_mb=12000, total_mb=16384)
    assert r["level"] in ("normal", "high", "critical")


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_optimize_bulk(app, i):
    r = await app.resource_optimization.optimize()
    assert r["accepted"] is True
    assert "battery_throttle" in r


@pytest.mark.parametrize("mode", list(MODES))
def test_set_mode_all(app, mode):
    cfg = app.resource_optimization.set_mode(mode)
    assert "max_context" in cfg


@pytest.mark.parametrize("i", range(12))
@pytest.mark.asyncio
async def test_optimize_mode_cycle(app, i):
    modes = list(MODES)
    app.resource_optimization.set_mode(modes[i % len(modes)])
    r = await app.resource_optimization.optimize()
    assert r["accepted"] is True


@pytest.mark.parametrize("on_battery", [True, False])
@pytest.mark.asyncio
async def test_battery_throttle(app, on_battery, monkeypatch):
    monkeypatch.setattr(app.settings, "on_battery", on_battery)
    r = await app.resource_optimization.optimize()
    assert r["battery_throttle"] <= 1.0


@pytest.mark.parametrize("battery_pct", [10, 25, 50, 75, 100])
def test_throttle_battery_pct(battery_pct):
    f = throttle_factor(on_battery=True, battery_pct=battery_pct)
    assert 0 < f <= 1.0


@pytest.mark.parametrize("used,total", [(1000, 16384), (8000, 16384), (14000, 16384), (16000, 16384)])
def test_pressure_ranges(used, total):
    r = pressure_level(used_mb=used, total_mb=total)
    assert "level" in r
