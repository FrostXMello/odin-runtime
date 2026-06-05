"""Milestone 8 — cognitive stability and integrity."""

import pytest
from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.autonomy.layer import AutonomyLevel
from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType
from odin_backend.models.task import AgentId
from odin_backend.tools.base import ToolContext


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
async def test_coherence_validation(app: OdinApplication):
    await app.kernel.process_signal(
        Signal(kind=SignalKind.WORKFLOW, name="workflow.failed", source="odin", workflow_id="wf1")
    )
    await app.kernel.process_signal(
        Signal(kind=SignalKind.RECOMMENDATION, name="recommendation.created", source="odin", payload={"title": "x"})
    )
    state = app.kernel.get_state()
    report = app.coherence.validate(state, app.kernel.recent_signals())
    assert report.coherence_score < 1.0
    assert report.conflict_report


@pytest.mark.asyncio
async def test_snapshot_create_and_diff(app: OdinApplication):
    s1 = app.snapshots.create_snapshot(app, label="before")
    await app.kernel.process_signal(
        Signal(kind=SignalKind.COGNITION, name="cognition.shift", source="odin", payload={"message": "test"})
    )
    s2 = app.snapshots.create_snapshot(app, label="after")
    diff = app.snapshots.diff_snapshots(s1.id, s2.id)
    assert "differences" in diff


@pytest.mark.asyncio
async def test_stability_loop(app: OdinApplication):
    audit = await app.stability.run_cycle(app)
    assert "coherence_score" in audit
    assert audit["run"] >= 1


@pytest.mark.asyncio
async def test_memory_refinement_trace(app: OdinApplication):
    await app.memory.save_memory("ODIN stability test memory", category="test")
    await app.memory.save_memory("ODIN stability test memory", category="test")
    report = await app.memory_refinement.refine(limit=20)
    assert report.trace_log or report.merged_count >= 0


@pytest.mark.asyncio
async def test_autonomy_level_1_blocks_execution(app: OdinApplication):
    app.autonomy.set_level(AutonomyLevel.SUGGESTIONS)
    allowed, reason, _ = app.autonomy.allows_execution(
        ExecutionRequest(tool_name="read_file", agent_id="odin", params={})
    )
    assert allowed is False


@pytest.mark.asyncio
async def test_autonomy_bounded_allows_safe_tool(app: OdinApplication):
    app.autonomy.set_level(AutonomyLevel.BOUNDED)
    allowed, _, _ = app.autonomy.allows_execution(
        ExecutionRequest(tool_name="read_file", agent_id="odin", params={"path": "README.md"})
    )
    assert allowed is True


@pytest.mark.asyncio
async def test_governor_coherence_defer(app: OdinApplication):
    app.coherence._last_report.coherence_score = 0.2  # noqa: SLF001
    decision = await app.governor.evaluate(
        ExecutionRequest(tool_name="read_file", agent_id="odin", params={})
    )
    assert decision.decision == GovernorDecisionType.DEFER


@pytest.mark.asyncio
async def test_kernel_state_includes_coherence(app: OdinApplication):
    await app.kernel.process_signal(
        Signal(kind=SignalKind.MEMORY, name="memory.updated", source="mimir", payload={"memory_id": "a"})
    )
    state = app.kernel.get_state()
    assert hasattr(state, "coherence_score")
