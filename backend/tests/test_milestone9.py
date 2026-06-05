"""Milestone 9 — data architecture & agent protocol."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.bus.signals import Signal, SignalKind, SignalSource
from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType
from odin_backend.models.agent_message import AgentMessage, AgentMessageType
from odin_backend.models.task import TaskCreate, TaskPriority
from odin_backend.models.task_graph import TaskNodeStatus
from odin_backend.memory.models import MemoryItem, MemoryItemType


@pytest.fixture
async def app():
    settings = Settings(
        runtime_enable_background_loops=False,
        stability_loop_enabled=False,
        default_autonomy_level=3,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_cognitive_state_ssot_fields(app: OdinApplication):
    state = app.kernel.get_state()
    for field in (
        "active_signals",
        "task_graph",
        "priority_queue",
        "coherence_snapshot",
        "autonomy_state",
        "memory_context",
        "active_agents",
        "execution_log",
        "system_health",
        "last_stability_check",
    ):
        assert hasattr(state, field)


@pytest.mark.asyncio
async def test_signal_universal_schema(app: OdinApplication):
    signal = Signal(
        kind=SignalKind.AGENT,
        name="agent.result",
        type="agent.result",
        source="mimir",
        source_kind=SignalSource.AGENT,
        priority=70,
        payload={"ok": True},
        context_refs=["task:t1"],
        requires_response=False,
    )
    state = await app.kernel.process_signal(signal)
    assert state.active_signals
    assert state.active_signals[-1]["type"] == "agent.result"


@pytest.mark.asyncio
async def test_task_graph_node_lifecycle(app: OdinApplication):
    n1 = app.kernel.add_task_node(goal="Research topic", assigned_agent="hugin")
    n2 = app.kernel.add_task_node(
        goal="Summarize findings",
        assigned_agent="munin",
        dependencies=[n1.id],
    )
    snap = app.kernel.task_graph.snapshot()
    assert snap["node_count"] == 2
    ready = app.kernel.task_graph.ready_nodes()
    assert len(ready) == 1
    assert ready[0].id == n1.id
    app.kernel.task_graph.update_status(n1.id, TaskNodeStatus.COMPLETE)
    ready2 = app.kernel.task_graph.ready_nodes()
    assert any(n.id == n2.id for n in ready2)


@pytest.mark.asyncio
async def test_agent_protocol_no_peer_routing(app: OdinApplication):
    with pytest.raises(ValueError):
        AgentMessage(
            from_agent="hugin",
            to_odin=False,
            type=AgentMessageType.REQUEST,
            payload={},
        )


@pytest.mark.asyncio
async def test_agent_message_through_protocol(app: OdinApplication):
    node = await app.agent_protocol.assign_task(
        goal="Test agent report",
        agent_id="mimir",
        task_id="task-proto-1",
    )
    result = await app.agent_protocol.receive_from_agent(
        AgentMessage(
            from_agent="mimir",
            type=AgentMessageType.RESULT,
            payload={"output": "done"},
            task_id=node.id,
        )
    )
    assert result["accepted"]
    updated = app.kernel.task_graph.get(node.id)
    assert updated.status == TaskNodeStatus.COMPLETE


@pytest.mark.asyncio
async def test_coherence_conflict_escalates(app: OdinApplication):
    app.coherence._last_report.conflict_report = ["test conflict"]  # noqa: SLF001
    decision = await app.governor.evaluate(
        ExecutionRequest(tool_name="read_file", agent_id="odin", params={})
    )
    assert decision.decision == GovernorDecisionType.ESCALATE_TO_USER


@pytest.mark.asyncio
async def test_execution_pipeline_trace(app: OdinApplication):
    result = await app.execution_contract.run_tool_pipeline(
        app,
        ExecutionRequest(
            tool_name="get_system_info",
            agent_id="mimir",
            params={},
            user_confirmed=False,
        ),
    )
    assert len(result.trace) >= 3
    state = app.kernel.get_state()
    assert state.execution_log


@pytest.mark.asyncio
async def test_memory_item_schema():
    item = MemoryItem(
        type=MemoryItemType.FACT,
        content={"text": "ODIN uses a task graph"},
        source="test",
    )
    assert item.type == MemoryItemType.FACT
    legacy = MemoryItem.from_legacy(
        memory_id="m1",
        text="hello",
        category="preference",
    )
    assert legacy.type == MemoryItemType.PREFERENCE


@pytest.mark.asyncio
async def test_orchestrator_mirrors_task_graph(app: OdinApplication):
    create = TaskCreate(
        title="Graph mirror test",
        description="Ensure task graph node exists",
        priority=TaskPriority.NORMAL,
        metadata={"domain": "memory"},
    )
    task = await app.agent_protocol.submit_orchestrator_task(app.orchestrator, create)
    node = app.kernel.task_graph.get(task.id)
    assert node is not None
    assert node.goal
    await app.orchestrator.cancel_task(task.id)
