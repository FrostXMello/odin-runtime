
"""Prompt 39 autonomous engineering workspace tests."""
from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
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
        intelligence_quality_enabled=True,
        advanced_retrieval_enabled=True,
        code_copilot_enabled=True,
        operator_intelligence_enabled=True,
        model_orchestration_enabled=True,
        autonomy_reliability_enabled=True,
        engineering_memory_enabled=True,
        autonomous_debugging_enabled=True,
        safe_patching_enabled=True,
        dev_workflows_enabled=True,
        validation_fabric_enabled=True,
        repository_graph_enabled=True,
        engineering_agents_enabled=True,
        engineering_workspace_enabled=True,
        local_ai_mode="balanced",
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_validate_patch(app):
    r = await app.validation_fabric.validate_patch(before="old", after="new", confidence=0.7)
    assert r["accepted"] is True


@pytest.mark.asyncio
async def test_create_goal(app):
    r = await app.dev_workflows.create_goal(title="Implement feature", repo="odin")
    assert r["accepted"] is True


def test_rollback_prepared_channel():
    ev = TraceEvent(kind=TraceEventKind.ROLLBACK_PREPARED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "patches:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_bulk(app, i):
    r = await app.validation_fabric.validate_patch(before=f"b{i}", after=f"a{i}", confidence=0.6)
    assert r["accepted"] is True


@pytest.mark.parametrize("j", range(12))
@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_bulk_matrix(app, i, j):
    r = await app.validation_fabric.validate_patch(before=f"b{i}", after=f"a{i}", confidence=0.6)
    assert r["accepted"] is True
