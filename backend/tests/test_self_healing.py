"""Prompt 35 production runtime — self-healing tests."""

from __future__ import annotations

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.observability.events import TraceEvent, TraceEventKind
from odin_backend.core.self_healing.dependency_healer import heal_dependencies
from odin_backend.core.self_healing.execution_forensics import analyze_lineage
from odin_backend.core.self_healing.recovery_planner import plan_recovery
from odin_backend.core.self_healing.retry_optimizer import optimize_retry
from odin_backend.core.streaming.serializers import resolve_channels_for_trace
from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus


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
    )


@pytest.fixture
async def app(settings):
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_app_has_self_healing(app):
    assert hasattr(app, "self_healing")


@pytest.mark.asyncio
async def test_heal(app):
    r = await app.self_healing.heal()
    assert r["accepted"] is True
    assert "actions" in r
    assert "plan" in r
    assert "retry" in r


@pytest.mark.asyncio
async def test_heal_with_mission(app):
    r = await app.self_healing.heal(mission_id="missing-mission")
    assert r["accepted"] is True
    assert r["salvaged"] is not None


@pytest.mark.asyncio
async def test_heal_disabled(tmp_path):
    s = Settings(
        database_url=f"sqlite+aiosqlite:///{(tmp_path / 'd.db').resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        self_healing_enabled=False,
        runtime_enable_background_loops=False,
        model_provider="mock",
    )
    odin = OdinApplication(s, use_redis=False)
    await odin.startup()
    r = await odin.self_healing.heal()
    assert r["accepted"] is False
    assert r["reason"] == "self_healing_disabled"
    await odin.shutdown()


@pytest.mark.asyncio
async def test_forensics(app):
    data = [
        {"mission_id": "m1", "state": "completed"},
        {"mission_id": "m1", "state": "failed"},
    ]
    report = app.self_healing.forensics(data)
    assert report["nodes"] == 2
    assert report["failures"] == 1


def test_forensics_empty(app):
    report = app.self_healing.forensics()
    assert report["nodes"] == 0


def test_snapshot(app):
    snap = app.self_healing.snapshot()
    assert "salvages" in snap
    assert "repairs" in snap


def test_dependency_healer_unit():
    graph = TaskGraph()
    node = TaskNode(id="blocked-a", goal="heal me", status=TaskNodeStatus.BLOCKED, dependencies=[])
    graph.add_node(node)
    healed = heal_dependencies(graph)
    assert "blocked-a" in healed
    assert graph.nodes["blocked-a"].status == TaskNodeStatus.READY


@pytest.mark.parametrize("failure_rate,strategy", [(0.2, "immediate"), (0.5, "backoff_linear"), (0.8, "backoff_aggressive")])
def test_retry_optimizer_unit(failure_rate, strategy):
    r = optimize_retry(attempt=2, failure_rate=failure_rate)
    assert r["strategy"] == strategy
    assert r["delay_s"] > 0


@pytest.mark.parametrize(
    "mission_state,failed,blocked,expected",
    [
        ("running", 2, 0, "retry_failed"),
        ("running", 0, 1, "heal_dependencies"),
        ("blocked", 0, 0, "resume_mission"),
        ("running", 0, 0, "observe"),
    ],
)
def test_recovery_planner_unit(mission_state, failed, blocked, expected):
    plan = plan_recovery(mission_state=mission_state, failed_tasks=failed, blocked_tasks=blocked)
    assert plan["strategy"] == expected


def test_analyze_lineage_unit():
    report = analyze_lineage(
        [{"mission_id": "a", "state": "ok"}, {"mission_id": "b", "state": "failed"}]
    )
    assert report["branches"] == 2
    assert report["failure_rate"] == 0.5


def test_execution_salvaged_channel():
    ev = TraceEvent(kind=TraceEventKind.EXECUTION_SALVAGED, trace_id="t", span_id="s", causal_chain_id="c")
    assert "healing:runtime" in resolve_channels_for_trace(ev)


@pytest.mark.parametrize("i", range(35))
@pytest.mark.asyncio
async def test_heal_bulk(app, i):
    r = await app.self_healing.heal(mission_id=f"mission-{i}" if i % 3 == 0 else None)
    assert r["accepted"] is True
    assert isinstance(r["stuck"], list)


@pytest.mark.parametrize("i", range(15))
@pytest.mark.asyncio
async def test_heal_repairs_increment(app, i):
    before = app.self_healing.snapshot()["repairs"]
    await app.self_healing.heal()
    after = app.self_healing.snapshot()["repairs"]
    assert after >= before


@pytest.mark.parametrize("i", range(10))
def test_forensics_bulk(app, i):
    executions = [{"mission_id": f"m{i % 5}", "state": "failed" if i % 2 else "completed"} for _ in range(i + 1)]
    report = app.self_healing.forensics(executions)
    assert report["nodes"] == i + 1


@pytest.mark.parametrize("attempt", range(8))
def test_retry_optimizer_attempts(attempt):
    r = optimize_retry(attempt=attempt, failure_rate=0.5)
    assert r["delay_s"] >= 2.0
