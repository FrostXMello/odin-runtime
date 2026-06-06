"""Prompt 37 production runtime — recovery and daily workflow tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.stability.recovery_report import build_recovery_report
from odin_backend.core.stability.safe_boot import safe_boot_plan
from odin_backend.core.storage_optimization.archival_policy import apply_archival, retention_policy
from odin_backend.core.storage_optimization.storage_analytics import analyze_storage
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


@pytest.fixture
def project_dir(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "main.py").write_text("print('hello')\n", encoding="utf-8")
    return root


async def _register(app, project_dir, *, name: str = "recovery-proj"):
    return await app.project_os.register_project(
        name=name,
        path=str(project_dir.resolve()),
    )


@pytest.mark.asyncio
async def test_recovery_report(app):
    r = await app.runtime_guardian.recovery_report()
    assert r["accepted"] is True
    assert "report" in r
    assert "guardian" in r["report"]
    assert "daemon" in r["report"]


@pytest.mark.asyncio
async def test_safe_boot(app):
    r = await app.runtime_guardian.safe_boot()
    assert r["accepted"] is True
    assert r["plan"]["mode"] == "safe"
    assert app.runtime_guardian.snapshot()["mode"] == "safe"


@pytest.mark.asyncio
async def test_safe_boot_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_guardian_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.runtime_guardian.safe_boot()
    assert r["accepted"] is False
    assert r["reason"] == "runtime_guardian_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_daily_startup_routine(app, project_dir):
    await _register(app, project_dir, name="daily-work")
    r = await app.daily_workflow.startup_routine()
    assert r["accepted"] is True
    assert isinstance(r["suggestions"], list)


@pytest.mark.asyncio
async def test_daily_startup_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        daily_driver_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.daily_workflow.startup_routine()
    assert r["accepted"] is False
    assert r["reason"] == "daily_driver_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_idle_consolidation(app):
    r = await app.daily_workflow.idle_consolidation()
    assert r["accepted"] is True
    assert "consolidated" in r


@pytest.mark.asyncio
async def test_storage_analytics(app):
    r = await app.storage_optimization.analytics()
    assert "cache_entries" in r
    assert "projects" in r


@pytest.mark.asyncio
async def test_apply_retention(app):
    r = await app.storage_optimization.apply_retention()
    assert r["accepted"] is True
    assert "analytics" in r
    assert "policy" in r


def test_build_recovery_report_unit():
    report = build_recovery_report(
        guardian={"degraded": False, "mode": "normal"},
        healing={"repairs": 0},
        daemon={"restarts": 0},
    )
    assert report["status"] == "healthy"


def test_safe_boot_plan_unit():
    plan = safe_boot_plan()
    assert plan["disable_background"] is True
    assert "minimal_models" in plan


def test_analyze_storage_unit():
    stats = analyze_storage(cache_size=100, cold_size=10, projects=3)
    assert stats["recommend_archive"] is False


def test_apply_archival_unit():
    policy = apply_archival(cache_entries=600)
    assert policy["archive"] is True


@pytest.mark.parametrize("age_days", [30, 60, 91, 120])
def test_retention_policy(age_days):
    pol = retention_policy(project_id="p1", age_days=age_days)
    assert pol["archive"] == (age_days > 90)


def test_recovery_completed_channel():
    ev = TraceEvent(
        kind=TraceEventKind.RECOVERY_COMPLETED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "diagnostics:runtime" in resolve_channels_for_trace(ev)


def test_watchdog_triggered_channel():
    ev = TraceEvent(
        kind=TraceEventKind.WATCHDOG_TRIGGERED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "stability:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(40))
@pytest.mark.asyncio
async def test_recovery_report_bulk(app, i):
    await app.runtime_guardian.supervise()
    r = await app.runtime_guardian.recovery_report()
    assert r["accepted"] is True
    assert r["report"]["status"] in ("healthy", "degraded")


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_safe_boot_bulk(app, i):
    r = await app.runtime_guardian.safe_boot()
    assert r["accepted"] is True
    assert r["plan"]["skip_heavy_subsystems"]


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_daily_startup_bulk(app, project_dir, i):
    await _register(app, project_dir, name=f"daily-{i}")
    r = await app.daily_workflow.startup_routine()
    assert r["accepted"] is True


@pytest.mark.parametrize("i", range(25))
@pytest.mark.asyncio
async def test_idle_consolidation_bulk(app, i):
    await app.vector_memory.ingest(f"consolidation probe {i}")
    r = await app.daily_workflow.idle_consolidation()
    assert r["accepted"] is True


@pytest.mark.parametrize("cache_size", [100, 300, 550, 800])
@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_storage_retention_matrix(app, cache_size, i):
    for _ in range(cache_size // 50):
        await app.vector_memory.ingest(f"retention-{i}-{_}")
    r = await app.storage_optimization.apply_retention()
    assert r["accepted"] is True
    assert "policy" in r


@pytest.mark.parametrize("i", range(20))
@pytest.mark.asyncio
async def test_storage_analytics_bulk(app, i):
    r = await app.storage_optimization.analytics()
    assert r["cache_entries"] >= 0
    assert r["cold_entries"] >= 0
