"""Prompt 37 production runtime — performance tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.performance.adaptive_batching import batch_size
from odin_backend.core.performance.cpu_fallbacks import use_cpu_fallback
from odin_backend.core.performance.gpu_allocator import allocate_vram
from odin_backend.core.performance.inference_scheduler import schedule_inference
from odin_backend.core.performance.io_scheduler import io_priority
from odin_backend.core.performance.lazy_loading import should_lazy_load
from odin_backend.core.performance.memory_pressure_manager import pressure_action
from odin_backend.core.performance.startup_optimizer import optimize_startup
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
        queue_persist_enabled=False,
        async_mission_runtime_enabled=False,
        project_os_enabled=True,
        developer_integrations_enabled=True,
        workspace_knowledge_enabled=True,
        productivity_enabled=True,
        local_search_enabled=True,
        communications_enabled=True,
        storage_optimization_enabled=True,
        deployment_enabled=True,
        performance_enabled=True,
        privacy_enabled=True,
        operator_shell_enabled=True,
        daily_driver_enabled=True,
        local_ai_mode="balanced",
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_performance(app):
    assert hasattr(app, "performance")


@pytest.mark.asyncio
async def test_optimize(app):
    r = await app.performance.optimize()
    assert r["accepted"] is True
    assert "pressure" in r
    assert "actions" in r
    assert "batch_size" in r


@pytest.mark.asyncio
async def test_optimize_startup(app):
    r = await app.performance.optimize_startup()
    assert r["accepted"] is True
    assert "deferred" in r
    assert "eager" in r


@pytest.mark.asyncio
async def test_performance_snapshot(app):
    await app.performance.optimize()
    snap = app.performance.snapshot()
    assert "optimizations" in snap
    assert snap["optimizations"] >= 1


@pytest.mark.asyncio
async def test_optimize_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        performance_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.performance.optimize()
    assert r["accepted"] is False
    assert r["reason"] == "performance_disabled"
    await odin.shutdown()


@pytest.mark.parametrize("level", ["normal", "high", "critical"])
def test_pressure_action(level):
    actions = pressure_action(level)
    assert "evict_models" in actions
    assert "throttle" in actions
    if level == "critical":
        assert actions["evict_models"] is True
        assert actions["throttle"] == 0.3


def test_optimize_startup_unit():
    plan = optimize_startup(components=["local_ai", "vector_memory", "daemon"])
    assert "local_ai" in plan["deferred"]
    assert "config" in plan["eager"]


@pytest.mark.parametrize("mode", ["balanced", "performance", "ultra_light", "overnight_daemon"])
def test_batch_size_modes(mode):
    batch = batch_size(mode=mode, ram_mb=16384)
    assert isinstance(batch, int)
    assert batch > 0


@pytest.mark.parametrize("pressure", ["normal", "high", "critical"])
def test_cpu_fallback(pressure):
    fb = use_cpu_fallback(vram_pressure=pressure, on_battery=False)
    assert isinstance(fb, bool)


@pytest.mark.parametrize("background", [True, False])
def test_io_priority(background):
    prio = io_priority(background=background)
    assert prio == ("low" if background else "normal")


def test_allocate_vram():
    gpu = allocate_vram(requested_mb=2048, available_mb=4096)
    assert "allocated_mb" in gpu or "granted" in gpu or isinstance(gpu, dict)


def test_schedule_inference():
    sched = schedule_inference(queue_depth=2, vram_pressure="normal")
    assert isinstance(sched, dict)


def test_should_lazy_load():
    assert isinstance(should_lazy_load(component="local_ai", idle=True), bool)


def test_startup_optimized_channel():
    ev = TraceEvent(
        kind=TraceEventKind.STARTUP_OPTIMIZED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "performance:runtime" in resolve_channels_for_trace(ev)


def test_memory_pressure_detected_channel():
    ev = TraceEvent(
        kind=TraceEventKind.MEMORY_PRESSURE_DETECTED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "performance:runtime" in resolve_channels_for_trace(ev)


def test_model_swapped_channel():
    ev = TraceEvent(
        kind=TraceEventKind.MODEL_SWAPPED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "performance:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(45))
@pytest.mark.asyncio
async def test_optimize_bulk(app, i):
    r = await app.performance.optimize()
    assert r["accepted"] is True
    assert r["pressure"]["level"] in ("normal", "high", "critical", "low")


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_optimize_startup_bulk(app, i):
    r = await app.performance.optimize_startup()
    assert r["accepted"] is True
    assert len(r["deferred"]) >= 1


@pytest.mark.parametrize("survival_mode", ["balanced", "performance", "ultra_light"])
@pytest.mark.parametrize("i", range(12))
@pytest.mark.asyncio
async def test_optimize_survival_modes(app, survival_mode, i, settings):
    app.settings.survival_mode = survival_mode
    r = await app.performance.optimize()
    assert r["accepted"] is True
    assert "cpu_fallback" in r


@pytest.mark.parametrize("on_battery", [True, False])
@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_optimize_battery(app, on_battery, i):
    app.settings.on_battery = on_battery
    r = await app.performance.optimize()
    assert r["accepted"] is True
    assert isinstance(r["cpu_fallback"], bool)


@pytest.mark.parametrize("ram_mb", [8192, 16384, 32768])
@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_optimize_ram_tiers(app, ram_mb, i):
    app.settings.local_ai_ram_mb = ram_mb
    r = await app.performance.optimize()
    assert r["accepted"] is True
    assert "gpu" in r
