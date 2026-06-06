"""Prompt 37 production runtime — deployment tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.deployment.config_profiles import PROFILES, profile_config
from odin_backend.deployment.dependency_manager import check_dependencies
from odin_backend.deployment.environment_validator import validate_environment
from odin_backend.deployment.hardware_detector import detect_hardware
from odin_backend.deployment.update_manager import migrate


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
    (root / "src").mkdir()
    (root / "main.py").write_text("print('hello')\n", encoding="utf-8")
    return root


async def _register(app, project_dir, *, name: str = "odin-deploy"):
    return await app.project_os.register_project(
        name=name,
        path=str(project_dir.resolve()),
    )


@pytest.mark.asyncio
async def test_app_has_deployment(app):
    assert hasattr(app, "deployment")
    assert hasattr(app, "performance")
    assert hasattr(app, "privacy")
    assert hasattr(app, "operator_shell")
    assert hasattr(app, "daily_workflow")


@pytest.mark.asyncio
async def test_validate(app):
    r = await app.deployment.validate()
    assert r["accepted"] is True
    assert "environment" in r
    assert "dependencies" in r
    assert "hardware" in r


@pytest.mark.asyncio
async def test_bootstrap(app):
    r = await app.deployment.bootstrap()
    assert r["accepted"] is True
    assert "profile" in r
    assert "config" in r
    assert "first_boot" in r


@pytest.mark.asyncio
async def test_export_restore_snapshot(app, project_dir):
    await _register(app, project_dir)
    exported = await app.deployment.export_snapshot()
    assert exported["accepted"] is True
    assert "snapshot_id" in exported
    restored = await app.deployment.restore_snapshot(exported["snapshot_id"])
    assert restored["accepted"] is True
    assert "state" in restored


@pytest.mark.asyncio
async def test_restore_snapshot_not_found(app):
    r = await app.deployment.restore_snapshot("missing-snapshot-id")
    assert r["accepted"] is False
    assert r["reason"] == "snapshot_not_found"


@pytest.mark.asyncio
async def test_upgrade(app):
    r = await app.deployment.upgrade(to_version="0.37.0")
    assert r["accepted"] is True
    assert r["migrated"] is True
    assert "steps" in r


@pytest.mark.asyncio
async def test_deployment_snapshot(app):
    await app.deployment.bootstrap(profile="balanced")
    snap = app.deployment.snapshot()
    assert snap["bootstrapped"] is True
    assert "profile" in snap
    assert "platform" in snap


@pytest.mark.asyncio
async def test_validate_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        deployment_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.deployment.validate()
    assert r["accepted"] is False
    assert r["reason"] == "deployment_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_bootstrap_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        deployment_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.deployment.bootstrap()
    assert r["accepted"] is False
    assert r["reason"] == "deployment_disabled"
    await odin.shutdown()


def test_validate_environment_unit():
    env = validate_environment()
    assert "valid" in env
    assert "python" in env


def test_check_dependencies_unit():
    deps = check_dependencies()
    assert "satisfied" in deps
    assert isinstance(deps["missing"], list)


@pytest.mark.parametrize("ram_mb,vram_mb,expected", [
    (8192, 2048, "ultra_light"),
    (16384, 4096, "ultra_light"),
    (32768, 8192, "performance"),
    (65536, 16384, "performance"),
])
def test_detect_hardware_profiles(ram_mb, vram_mb, expected):
    hw = detect_hardware(ram_mb=ram_mb, vram_mb=vram_mb)
    assert hw["ram_mb"] == ram_mb
    assert hw["vram_mb"] == vram_mb
    if expected != "apple_silicon":
        assert hw["recommended_profile"] in (expected, "apple_silicon", "balanced")


@pytest.mark.parametrize("profile", list(PROFILES.keys()))
def test_profile_config(profile):
    cfg = profile_config(profile)
    assert "resource_mode" in cfg
    assert "survival_mode" in cfg


def test_migrate_unit():
    r = migrate("0.36.0", "0.37.0")
    assert r["migrated"] is True
    assert r["from"] == "0.36.0"
    assert r["to"] == "0.37.0"


def test_deployment_validated_channel():
    ev = TraceEvent(
        kind=TraceEventKind.DEPLOYMENT_VALIDATED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "deployment:runtime" in resolve_channels_for_trace(ev)


def test_runtime_profile_changed_channel():
    ev = TraceEvent(
        kind=TraceEventKind.RUNTIME_PROFILE_CHANGED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "deployment:runtime" in resolve_channels_for_trace(ev)


def test_snapshot_restored_channel():
    ev = TraceEvent(
        kind=TraceEventKind.SNAPSHOT_RESTORED,
        trace_id="t",
        span_id="s",
        causal_chain_id="c",
    )
    assert "deployment:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(40))
@pytest.mark.asyncio
async def test_validate_bulk(app, i):
    r = await app.deployment.validate()
    assert r["accepted"] is True
    assert r["valid"] == (r["environment"]["valid"] and r["dependencies"]["satisfied"])


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_bootstrap_bulk(app, i):
    r = await app.deployment.bootstrap()
    assert r["accepted"] is True
    assert r["profile"] in PROFILES


@pytest.mark.parametrize("i", range(30))
@pytest.mark.asyncio
async def test_export_bulk(app, project_dir, i):
    await _register(app, project_dir, name=f"export-{i}")
    r = await app.deployment.export_snapshot()
    assert r["accepted"] is True
    assert r["exported"] is True


@pytest.mark.parametrize("profile", list(PROFILES.keys()))
@pytest.mark.parametrize("i", range(10))
@pytest.mark.asyncio
async def test_bootstrap_profile_matrix(app, profile, i):
    r = await app.deployment.bootstrap(profile=profile)
    assert r["accepted"] is True
    assert r["profile"] == profile
    assert r["config"] == profile_config(profile)


@pytest.mark.parametrize("version", ["0.35.0", "0.36.0", "0.37.0", "0.38.0"])
@pytest.mark.parametrize("i", range(8))
@pytest.mark.asyncio
async def test_upgrade_versions(app, version, i):
    r = await app.deployment.upgrade(to_version=version)
    assert r["accepted"] is True
    assert r["to"] == version
