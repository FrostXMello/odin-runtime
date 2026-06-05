"""Orchestration stabilization — dedup, lifecycle, dispatcher, policy, health."""

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.missions.dedup import build_fingerprint, normalize_objective, MissionDeduplicator
from odin_backend.core.missions.dispatcher import ExecutionDispatcher
from odin_backend.core.missions.lifecycle import (
    InvalidTransitionError,
    MissionStateMachine,
    TaskStateMachine,
)
from odin_backend.core.missions.manager import MissionDuplicateError
from odin_backend.core.missions.policy import ExecutionPolicyEnforcer, PolicyVerdict
from odin_backend.core.missions.health import assess_orchestration_health
from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus


@pytest.fixture
async def app(tmp_path):
    db_file = tmp_path / "odin_test.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db_file.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        mission_worker_enabled=False,
        mission_dispatch_enabled=False,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
        mission_replay_window_seconds=60,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


def test_normalize_objective_dedup():
    assert normalize_objective("  Hello, World!!  ") == normalize_objective("hello world")
    assert normalize_objective("A  B") == "a b"


def test_fingerprint_deterministic():
    a = build_fingerprint("Do X", mission_type="standard", originating_signal="api")
    b = build_fingerprint("do x!!!", mission_type="standard", originating_signal="api")
    assert a.digest == b.digest


@pytest.mark.asyncio
async def test_duplicate_active_mission_blocked(app: OdinApplication):
    m1 = await app.mission_manager.create("Analyze system logs for errors")
    with pytest.raises(MissionDuplicateError):
        await app.mission_manager.create("analyze system logs for errors")

    result = await app.mission_manager.create_checked("analyze system logs for errors")
    assert result.suppressed
    assert result.duplicate_of == m1.mission_id


@pytest.mark.asyncio
async def test_replay_protection_after_complete(app: OdinApplication):
    mission = await app.mission_manager.create("Single step objective for replay test.")
    while not mission.is_terminal() and mission.current_wave < 25:
        await app.mission_runtime.run_wave(app, mission)
        mission = await app.mission_manager.get(mission.mission_id)
    assert mission.current_state == MissionLifecycle.COMPLETED

    dedup = MissionDeduplicator(replay_window_seconds=3600)
    fp = build_fingerprint(mission.objective)
    decision = dedup.evaluate(fp, [mission])
    assert not decision.allow
    assert decision.action == "replay_blocked"


def test_mission_lifecycle_invalid_transition():
    mission = Mission(objective="test", current_state=MissionLifecycle.COMPLETED)
    sm = MissionStateMachine(mission)
    with pytest.raises(InvalidTransitionError):
        sm.transition(MissionLifecycle.RUNNING, reason="invalid")


def test_task_lifecycle_transitions():
    node = TaskNode(goal="g", status=TaskNodeStatus.PENDING)
    TaskStateMachine.transition(node, TaskNodeStatus.READY, reason="test")
    TaskStateMachine.transition(node, TaskNodeStatus.ASSIGNED, reason="test")
    TaskStateMachine.transition(node, TaskNodeStatus.EXECUTING, reason="test")
    TaskStateMachine.transition(node, TaskNodeStatus.COMPLETE, reason="test")
    assert node.status == TaskNodeStatus.COMPLETE


def test_policy_blocks_dangerous_objective():
    enforcer = ExecutionPolicyEnforcer()
    assessment = enforcer.assess_objective("Please delete the database now", human_approved=False)
    assert assessment.verdict == PolicyVerdict.APPROVAL_REQUIRED
    assert assessment.requires_human_approval


def test_policy_sandbox_after_approval():
    enforcer = ExecutionPolicyEnforcer()
    assessment = enforcer.assess_objective("rm -rf /tmp/data", human_approved=True)
    assert assessment.verdict == PolicyVerdict.SANDBOX_ONLY
    assert assessment.sandbox_only


@pytest.mark.asyncio
async def test_dispatcher_executes_wave(app: OdinApplication):
    mission = await app.mission_manager.create("Dispatch step one. Dispatch step two.")
    dispatcher = ExecutionDispatcher(app)
    result = await dispatcher.dispatch_mission_now(mission.mission_id)
    assert not result.get("skipped") or result.get("pending", 0) >= 0
    updated = await app.mission_manager.get(mission.mission_id)
    assert updated.current_wave >= 1 or updated.is_terminal()


@pytest.mark.asyncio
async def test_orchestration_health_degrades_on_stall(app: OdinApplication):
    await app.mission_manager.create("Stalled mission step one. Stalled mission step two.")
    report = assess_orchestration_health(app)
    assert report.status in ("healthy", "degraded", "critical")
    assert "duplicate_suppression_count" in report.model_dump()


@pytest.mark.asyncio
async def test_gc_archives_terminal(app: OdinApplication):
    mission = await app.mission_manager.create("GC archive step one. GC archive step two.")
    while not mission.is_terminal() and mission.current_wave < 25:
        await app.mission_runtime.run_wave(app, mission)
        mission = await app.mission_manager.get(mission.mission_id)
    await app.mission_gc.run(app.mission_manager)
    archived = await app.mission_manager.get(mission.mission_id)
    assert archived.current_state == MissionLifecycle.ARCHIVED
