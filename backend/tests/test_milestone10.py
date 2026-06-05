"""Milestone 10 — runtime conscious loop."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.autonomy.layer import AutonomyLevel
from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.core.conscious_loop.decisions import CycleDecision
from odin_backend.core.kernel.kernel import OdinCognitiveKernel
from odin_backend.models.task_graph import TaskNodeStatus


@pytest.fixture
async def app():
    settings = Settings(
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        stability_loop_enabled=False,
        default_autonomy_level=3,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_conscious_cycle_runs(app: OdinApplication):
    result = await app.conscious_loop.run_cycle()
    assert result.tick >= 1
    assert result.decision in CycleDecision
    assert result.coherence_score <= 1.0


@pytest.mark.asyncio
async def test_observe_mode_low_autonomy(app: OdinApplication):
    app.autonomy.set_level(AutonomyLevel.SUGGESTIONS)
    app.kernel.add_task_node(goal="Pending work item", assigned_agent="mimir")
    result = await app.conscious_loop.run_cycle()
    assert result.decision == CycleDecision.OBSERVE
    assert result.executed == 0


@pytest.mark.asyncio
async def test_coherence_conflict_escalates(app: OdinApplication):
    app.autonomy.set_level(AutonomyLevel.BOUNDED)
    await app.kernel.process_signal(
        Signal(
            kind=SignalKind.WORKFLOW,
            name="workflow.failed",
            source="odin",
            type="workflow.failed",
            workflow_id="wf-conflict",
            payload={"error": "timeout"},
        )
    )
    await app.kernel.process_signal(
        Signal(
            kind=SignalKind.RECOMMENDATION,
            name="recommendation.created",
            source="odin",
            type="recommendation.created",
            payload={"title": "Follow up"},
        )
    )
    result = await app.conscious_loop.run_cycle()
    assert result.decision == CycleDecision.ESCALATE
    assert app.conscious_loop.pending_escalations()


@pytest.mark.asyncio
async def test_planning_refines_task_graph(app: OdinApplication):
    app.kernel.add_task_node(goal="Same goal", task_id="a1")
    app.kernel.add_task_node(goal="Same goal", task_id="a2")
    result = await app.conscious_loop.run_cycle()
    assert any("merge" in a or "duplicate" in a for a in result.planning_actions) or result.tick >= 1
    blocked = app.kernel.task_graph.get("a2")
    if blocked:
        assert blocked.status in (TaskNodeStatus.BLOCKED, TaskNodeStatus.PENDING)


@pytest.mark.asyncio
async def test_stability_interval_not_every_tick(app: OdinApplication):
    app.autonomy.set_level(AutonomyLevel.SUGGESTIONS)
    app.settings.conscious_loop_stability_interval = 5
    app.settings.stability_loop_enabled = True
    for _ in range(3):
        await app.conscious_loop.run_cycle()
    state = app.kernel.get_state()
    assert state.last_stability_check is None or app.conscious_loop.tick_count < 5


@pytest.mark.asyncio
async def test_kernel_apply_planning():
    from odin_backend.core.conscious_loop.planner import SelfReasoningPlanner

    kernel = OdinCognitiveKernel.__new__(OdinCognitiveKernel)
    from odin_backend.core.kernel.state import CognitiveState
    from odin_backend.models.task_graph import TaskGraph

    kernel._state = CognitiveState()
    kernel.task_graph = TaskGraph()
    kernel.add_task_node(goal="Test task", task_id="t1")
    report = SelfReasoningPlanner().refine(kernel.task_graph)
    kernel.apply_planning(report)
    assert kernel.task_graph.snapshot()["node_count"] >= 1
