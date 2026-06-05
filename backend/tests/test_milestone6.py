"""Milestone 6 — persistent AI operating environment."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.desktop_runtime.events import DesktopEventType
from odin_backend.models.task import AgentId


@pytest.fixture
async def app():
    settings = Settings(
        runtime_enable_background_loops=False,
        context_awareness_enabled=True,
        desktop_collector_enabled=True,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_desktop_runtime_ingest(app: OdinApplication):
    await app.desktop_runtime.set_enabled(True)
    result = await app.desktop_runtime.ingest_snapshot(
        {
            "active_app": "Code",
            "active_window": {"title": "engine.py"},
            "vscode": {"workspace": "./odin"},
            "browser_tabs": [{"url": "https://github.com", "title": "ODIN"}],
        },
        collector="test",
    )
    assert result["accepted"] is True
    assert app.context_engine.get_session() is not None


@pytest.mark.asyncio
async def test_workspace_intelligence(app: OdinApplication):
    await app.context_engine.update_environment(
        application="Code",
        window="debug error",
        terminal_output="Exception in thread",
    )
    summary = app.workspace_intelligence.summarize_workspace(app.context_engine.get_session())
    assert "session_type" in summary
    assert summary["primary_project"]


@pytest.mark.asyncio
async def test_live_cognition_attention(app: OdinApplication):
    await app.live_cognition.ingest_context_shift("Focus shifted to runtime debugging")
    attention = app.live_cognition.get_current_attention()
    assert len(attention) >= 1
    state = app.live_cognition.summarize_operational_state()
    assert "workspace" in state


@pytest.mark.asyncio
async def test_resilience_circuit_breaker(app: OdinApplication):
    assert app.resilience.is_tool_available("failing_tool") is True
    for _ in range(6):
        app.resilience.record_tool_failure("failing_tool")
    assert app.resilience.is_tool_available("failing_tool") is False


@pytest.mark.asyncio
async def test_agent_society_routing(app: OdinApplication):
    agent = app.agent_society.route_task("research")
    assert agent == AgentId.HUGIN
    profiles = app.agent_society.list_profiles()
    assert len(profiles) >= 1


@pytest.mark.asyncio
async def test_memory_evolution_timeline(app: OdinApplication):
    await app.memory_evolution.record_operational_event("workflow", "Test run completed")
    timeline = app.memory_evolution.get_behavioral_timeline(5)
    assert len(timeline) >= 1


@pytest.mark.asyncio
async def test_compute_dashboard(app: OdinApplication):
    dash = app.compute.runtime_dashboard()
    assert "local_models" in dash


@pytest.mark.asyncio
async def test_trust_assessment(app: OdinApplication):
    assessment = await app.trust_system.assess_execution(
        "execute_terminal",
        params={"command": "ls", "cwd": "/tmp"},
    )
    assert assessment.risk_level in ("low", "medium", "high")
    assert assessment.explanation


@pytest.mark.asyncio
async def test_workspace_automation_actions(app: OdinApplication):
    await app.context_engine.update_environment(application="Code", window="app.py")
    actions = app.workspace_automation.generate_actions(app.context_engine.get_session())
    assert len(actions["actions"]) >= 2
    assert actions["explainable"]["requires_approval"] is True


@pytest.mark.asyncio
async def test_preference_evolution(app: OdinApplication):
    await app.preference_evolution.record_interaction("workflow")
    style = app.preference_evolution.adapt_response_style()
    assert style["transparent"] is True
