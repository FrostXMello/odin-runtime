"""Milestone 5 — ambient cognitive operating layer."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.models.task import AgentId
from odin_backend.policies.engine import PolicyEngine
from odin_backend.tools.base import ToolContext


@pytest.fixture
async def app():
    settings = Settings(
        runtime_enable_background_loops=False,
        context_awareness_enabled=True,
        proactive_recommendations_enabled=True,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_context_engine_session(app: OdinApplication):
    session = await app.context_engine.update_environment(
        application="Code",
        window="odin_backend",
        project="PROJECT_ODIN",
        repository="./odin",
    )
    assert session is not None
    assert "PROJECT_ODIN" in (session.insight or "")
    snap = await app.context_engine.save_context_snapshot()
    assert snap.summary


@pytest.mark.asyncio
async def test_desktop_semantics_summary(app: OdinApplication):
    await app.context_engine.update_environment(
        application="Visual Studio Code",
        window="planner.py",
    )
    summary = app.desktop_semantics.summarize_current_workspace(app.context_engine.get_session())
    assert summary["session_type"] in ("development", "general", "research")


@pytest.mark.asyncio
async def test_execution_intelligence_reliability(app: OdinApplication):
    app.execution_intelligence.record_tool_execution("search_web", success=False, latency_ms=100)
    app.execution_intelligence.record_tool_execution("search_web", success=True, latency_ms=50)
    rec = app.execution_intelligence.recommend_for_tool("search_web")
    assert "recommended_tool" in rec


@pytest.mark.asyncio
async def test_collaboration_chain(app: OdinApplication):
    chain = app.collaboration.create_chain("research_report", "Analyze ODIN architecture")
    assert chain and len(chain.steps) == 4
    tasks = app.collaboration.build_tasks_for_chain(chain)
    assert tasks[0].assigned_agent == AgentId.HUGIN


@pytest.mark.asyncio
async def test_unified_cognitive_stream(app: OdinApplication):
    from odin_backend.cognitive_stream.aggregator import CognitiveSource

    entry = await app.unified_cognition.ingest(
        "Observing context shift",
        source=CognitiveSource.CONTEXT_SHIFT,
    )
    timeline = app.unified_cognition.timeline(5)
    assert any(e["id"] == entry["id"] for e in timeline)


@pytest.mark.asyncio
async def test_memory_consolidation(app: OdinApplication):
    await app.memory.save_memory("ODIN workflow test pattern", category="workflow")
    await app.memory.save_memory("ODIN workflow test pattern", category="workflow")
    report = await app.memory_consolidation.run_consolidation_pass()
    assert "duplicate_groups" in report


@pytest.mark.asyncio
async def test_proactive_recommendations(app: OdinApplication):
    await app.context_engine.update_environment(
        application="Chrome",
        tabs=[
            {"url": "https://github.com/odin", "title": "ODIN"},
            {"url": "https://docs.python.org", "title": "Python"},
            {"url": "https://ollama.com", "title": "Ollama"},
        ],
    )
    recs = await app.proactive.generate_recommendations()
    assert len(recs) >= 1
    expl = app.proactive.explain(recs[0].id)
    assert expl and expl.get("requires_approval_to_execute") is True


@pytest.mark.asyncio
async def test_local_models_status(app: OdinApplication):
    status = app.local_models.runtime_status()
    assert "default_model" in status


@pytest.mark.asyncio
async def test_policy_engine_terminal_block(app: OdinApplication):
    decision = await app.policy_engine.evaluate(
        "execute_terminal",
        params={"command": "rm -rf /", "cwd": "/tmp"},
    )
    assert decision.allowed is False
    expl = app.policy_engine.explain_block(decision)
    assert expl["blocked"] is True
