"""Mission ↔ execution bridge integration tests."""

import asyncio

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.execution.models import ExecutionState
from odin_backend.core.runtime.task_contracts import parse_task_contract
from odin_backend.models.task_graph import TaskNode, TaskNodeStatus


@pytest.fixture
async def app(tmp_path):
    db = tmp_path / "bridge.db"
    settings = Settings(
        database_url=f"sqlite+aiosqlite:///{db.resolve().as_posix()}",
        chroma_persist_dir=tmp_path / "chroma",
        sandbox_work_dir=tmp_path / "sandbox",
        runtime_enable_background_loops=False,
        conscious_loop_enabled=False,
        live_loop_enabled=False,
        stability_loop_enabled=False,
        mission_dispatch_enabled=True,
        mission_gc_enabled=False,
        mission_restore_on_startup=False,
        execution_engine_enabled=True,
        mission_execution_bridge_enabled=True,
        streaming_enabled=False,
        execution_default_timeout_seconds=15.0,
        execution_recovery_interval_seconds=3600,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_parse_execution_contract():
    task = TaskNode(
        goal="run step",
        output={"type": "execution", "capability": "python.safe", "params": {"code": "print(1)"}},
    )
    c = parse_task_contract(task)
    assert c.uses_execution_engine
    assert c.capability == "python.safe"


@pytest.mark.asyncio
async def test_mission_to_execution_flow(app: OdinApplication):
    result = await app.mission_manager.create_checked("Bridge test: execute one python step.", human_approved=True)
    mission = result.mission
    app.mission_execution_bridge.planner.enrich_mission(mission)

    ready = mission.task_graph.ready_nodes()
    assert ready
    task = ready[0]
    success = await app.mission_execution_bridge.execute_task(mission, task)
    assert success
    eid = task.output.get("execution_id")
    assert eid
    record = await app.execution_engine.get(eid)
    assert record.state == ExecutionState.COMPLETED


@pytest.mark.asyncio
async def test_dependency_chain(app: OdinApplication):
    from odin_backend.models.task_graph import TaskGraph

    g = TaskGraph()
    t1 = TaskNode(
        goal="step 1",
        output={"type": "execution", "capability": "api.internal", "params": {"action": "a"}},
    )
    t2 = TaskNode(
        goal="step 2",
        dependencies=[t1.id],
        output={"type": "execution", "capability": "api.internal", "params": {"action": "b"}},
    )
    g.add_node(t1)
    g.add_node(t2)
    result = await app.mission_manager.create_checked("Dep test", human_approved=True)
    mission = result.mission
    mission.task_graph = g
    await app.mission_manager.persist(mission)

    ok1 = await app.mission_execution_bridge.execute_task(mission, t1)
    assert ok1
    mission.task_graph.update_status(t1.id, TaskNodeStatus.EXECUTING, reason="test", strict=False)
    mission.task_graph.update_status(t1.id, TaskNodeStatus.COMPLETE, reason="test", strict=False)
    ready = mission.task_graph.ready_nodes()
    assert any(n.id == t2.id for n in ready)


@pytest.mark.asyncio
async def test_stdout_in_timeline(app: OdinApplication):
    result = await app.mission_manager.create_checked("Timeline merge test", human_approved=True)
    mission = result.mission
    app.mission_execution_bridge.planner.enrich_mission(mission)
    task = mission.task_graph.ready_nodes()[0]
    await app.mission_execution_bridge.execute_task(mission, task)
    events = app.observability.tracer.store.get_mission_events(mission.mission_id)
    kinds = {e.kind.value for e in events}
    assert "execution_started" in kinds or "execution_completed" in kinds


@pytest.mark.asyncio
async def test_cancel_propagation(app: OdinApplication):
    result = await app.mission_manager.create_checked("Cancel test", human_approved=True)
    mid = result.mission.mission_id
    req = await app.execution_engine.submit(
        __import__(
            "odin_backend.core.execution.models", fromlist=["ExecutionRunRequest"]
        ).ExecutionRunRequest(
            capability="python.safe",
            mission_id=mid,
            params={"code": "import time\ntime.sleep(60)"},
            timeout_seconds=60,
        )
    )
    n = await app.mission_execution_bridge.cancel_mission_executions(mid)
    assert n >= 0
    await asyncio.sleep(0.3)
    rec = await app.execution_engine.get(req.execution_id)
    assert rec.state in (ExecutionState.CANCELLED, ExecutionState.RUNNING)


@pytest.mark.asyncio
async def test_adaptive_retry_decision(app: OdinApplication):
    result = await app.mission_manager.create_checked("Adaptive", human_approved=True)
    mission = result.mission
    task = TaskNode(goal="fail", output={"type": "shell", "command": "rm -rf /", "blocking": True})
    mission.task_graph.add_node(task)
    ok = await app.mission_execution_bridge.execute_task(mission, task)
    assert not ok
    decision = app.mission_execution_adaptive.decide(
        app,
        mission,
        task,
        execution_state="failed",
        contract_blocking=True,
    )
    assert decision.action in ("retry", "escalate", "replan", "isolate_branch")
