
"""Prompt 42 self-development loop tests."""
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
        context_fusion_enabled=True,
        workstation_awareness_enabled=True,
        continuous_cognition_enabled=True,
        execution_coordination_enabled=True,
        workflow_intelligence_enabled=True,
        live_copilot_enabled=True,
        cognitive_pipeline_enabled=True,
        cognitive_continuity_enabled=True,
        cognitive_shell_enabled=True,
        conversation_runtime_enabled=True,
        presence_enabled=True,
        cognitive_visualization_enabled=True,
        live_overlay_enabled=True,
        self_development_enabled=True,
        transparency_enabled=True,
        cognitive_interface_mode="balanced",
        self_evolution_enabled=True,
        self_improvement_memory_enabled=True,
        autonomous_patching_loop_enabled=True,
        runtime_benchmarks_enabled=True,
        evolution_governance_enabled=True,
        self_optimizing_routing_enabled=True,
        evolution_approval_level="proposal_only",
        self_evolution_mode="balanced",
        local_ai_mode="balanced",
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_memory_outcome(app):
    r = await app.self_improvement_memory.record_outcome(outcome="success", delta=0.05)
    assert r["accepted"] is True
    recent = await app.self_improvement_memory.recent(limit=5)
    assert len(recent) >= 1


@pytest.mark.asyncio
async def test_architecture_timeline(app):
    await app.self_improvement_memory.record_decision(title="branch isolation", rationale="no main commits")
    r = await app.self_improvement_memory.architecture_timeline()
    assert r["accepted"] is True
    assert len(r["timeline"]) >= 1


@pytest.mark.parametrize("i", range(45))
@pytest.mark.asyncio
async def test_bulk(app, i):
    r = await app.self_improvement_memory.record_outcome(outcome="success", delta=0.01 * i)
    assert r["accepted"] is True


@pytest.mark.parametrize("j", range(14))
@pytest.mark.parametrize("i", range(45))
@pytest.mark.asyncio
async def test_bulk_matrix(app, i, j):
    r = await app.self_improvement_memory.record_outcome(outcome="success", delta=0.01 * i)
    assert r["accepted"] is True
