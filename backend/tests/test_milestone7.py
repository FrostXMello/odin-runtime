"""Milestone 7 — ODIN cognitive kernel."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType
from odin_backend.core.app import OdinApplication
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.tools.base import ToolContext


@pytest.fixture
async def app():
    settings = Settings(runtime_enable_background_loops=False)
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_kernel_processes_signal(app: OdinApplication):
    signal = Signal(
        kind=SignalKind.WORKFLOW,
        name="workflow.failed",
        source="odin",
        workflow_id="wf-test-1",
        priority_hint=0.95,
        payload={"error": "step timeout"},
    )
    state = await app.kernel.process_signal(signal)
    assert state.current_focus
    assert state.signal_count >= 1
    assert state.graph_summary.get("nodes", 0) >= 1


@pytest.mark.asyncio
async def test_global_context_graph_updates(app: OdinApplication):
    signal = Signal(
        kind=SignalKind.MEMORY,
        name="memory.updated",
        source="mimir",
        payload={"memory_id": "mem-123", "category": "test"},
    )
    await app.kernel.process_signal(signal)
    snap = app.context_graph.snapshot()
    assert snap["node_count"] >= 3


@pytest.mark.asyncio
async def test_priority_strict_ranking(app: OdinApplication):
    for i in range(15):
        await app.kernel.process_signal(
            Signal(
                kind=SignalKind.RECOMMENDATION,
                name="recommendation.created",
                source="odin",
                payload={"title": f"Rec {i}", "relevance": 0.3 + i * 0.04},
            )
        )
    ranked = app.priority_engine.rank()
    assert len(ranked) <= 10


@pytest.mark.asyncio
async def test_governor_denies_high_risk_without_confirm(app: OdinApplication):
    decision = await app.governor.evaluate(
        ExecutionRequest(
            tool_name="execute_terminal",
            agent_id="brokk",
            params={"command": "ls"},
            user_confirmed=False,
        )
    )
    assert decision.decision == GovernorDecisionType.ESCALATE_TO_USER


@pytest.mark.asyncio
async def test_governor_approves_read_only(app: OdinApplication):
    decision = await app.governor.evaluate(
        ExecutionRequest(
            tool_name="read_file",
            agent_id="odin",
            params={"path": "./README.md"},
            user_confirmed=False,
        )
    )
    assert decision.decision == GovernorDecisionType.APPROVE


@pytest.mark.asyncio
async def test_signal_bus_routes_through_kernel(app: OdinApplication):
    before = app.kernel.get_state().signal_count
    await app.event_bus.publish(
        Event(
            type=EventType.WORKFLOW_COMPLETED,
            source=AgentId.ODIN,
            workflow_id="wf-bus-1",
            payload={"status": "completed"},
        )
    )
    after = app.kernel.get_state().signal_count
    assert after > before


@pytest.mark.asyncio
async def test_tool_execution_requires_governor(app: OdinApplication):
    ctx = ToolContext(agent_id=AgentId.BROKK, correlation_id="test")
    result = await app.tool_executor.execute(
        "execute_terminal",
        {"command": "echo test", "cwd": "/tmp"},
        ctx,
    )
    assert result.success is False
    assert "Governor" in (result.errors[0] if result.errors else "")


@pytest.mark.asyncio
async def test_kernel_explain(app: OdinApplication):
    expl = app.kernel.explain()
    assert "kernel" in expl["architecture"].lower()
