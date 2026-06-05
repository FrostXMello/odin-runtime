"""Prompt 35 production runtime — resource survival tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.resource_optimization.survival_modes import SURVIVAL_MODES, survival_config
from odin_backend.core.resource_optimization.emergency_reclaim import emergency_reclaim


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
async def test_survive_balanced(app):
    r = await app.resource_optimization.survive()
    assert r["accepted"] is True
    assert r["survival_mode"] == "balanced"
    assert "config" in r


@pytest.mark.asyncio
async def test_survive_ultra_light(app):
    r = await app.resource_optimization.survive(mode="ultra_light")
    assert r["accepted"] is True
    assert r["survival_mode"] == "ultra_light"
    assert r["config"]["max_models"] == 1
    assert "reclaimed" in r


@pytest.mark.asyncio
async def test_survive_overnight_daemon(app):
    r = await app.resource_optimization.survive(mode="overnight_daemon")
    assert r["accepted"] is True
    assert r["survival_mode"] == "overnight_daemon"
    assert r["config"].get("idle_compact") is True


@pytest.mark.asyncio
async def test_survive_performance(app):
    r = await app.resource_optimization.survive(mode="performance")
    assert r["accepted"] is True
    assert r["config"]["cognition_depth"] == 3


@pytest.mark.asyncio
async def test_survive_disabled(tmp_path):
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
    r = await odin.resource_optimization.survive()
    assert r["accepted"] is False
    await odin.shutdown()


@pytest.mark.asyncio
async def test_snapshot_survival_config(app):
    snap = app.resource_optimization.snapshot()
    assert snap["survival_mode"] == "balanced"
    assert "survival_config" in snap
    assert snap["survival_config"]["vram_cap_mb"] == 4096


@pytest.mark.asyncio
async def test_emergency_reclaim(app):
    await app.local_ai.warm_load("mock-reasoning")
    reclaimed = await emergency_reclaim(app)
    assert "count" in reclaimed
    assert isinstance(reclaimed["reclaimed"], list)


@pytest.mark.parametrize("mode", list(SURVIVAL_MODES))
def test_survival_config_unit(mode):
    cfg = survival_config(mode)
    assert "vram_cap_mb" in cfg
    assert "max_models" in cfg
    assert cfg["vram_cap_mb"] > 0


def test_survival_config_unknown_defaults_balanced():
    cfg = survival_config("unknown_mode")
    assert cfg == survival_config("balanced")


@pytest.mark.parametrize("mode,expected_models", [("ultra_light", 1), ("balanced", 2), ("performance", 3)])
def test_survival_modes_max_models(mode, expected_models):
    assert survival_config(mode)["max_models"] == expected_models


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_survive_bulk(app, i):
    mode = list(SURVIVAL_MODES.keys())[i % len(SURVIVAL_MODES)]
    r = await app.resource_optimization.survive(mode=mode)
    assert r["accepted"] is True
    assert r["survival_mode"] == mode


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_survive_ultra_light_bulk(app, i):
    r = await app.resource_optimization.survive(mode="ultra_light")
    assert r["config"]["batch_size"] == 1


@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_survive_overnight_bulk(app, i):
    r = await app.resource_optimization.survive(mode="overnight_daemon")
    assert r["config"]["idle_compact"] is True


@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_optimize_after_survive(app, i):
    await app.resource_optimization.survive(mode="balanced")
    r = await app.resource_optimization.optimize()
    assert r["accepted"] is True


@pytest.mark.parametrize("vram_cap", [2048, 4096, 6144])
def test_survival_vram_caps(vram_cap):
    for mode, cfg in SURVIVAL_MODES.items():
        if cfg["vram_cap_mb"] == vram_cap:
            assert survival_config(mode)["vram_cap_mb"] == vram_cap
            break
    else:
        pytest.skip("no mode with requested vram cap")
