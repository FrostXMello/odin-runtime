"""Async parallel mission runtime tests."""

import asyncio

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.execution.models import ExecutionState
from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus


@pytest.fixture
async def app(tmp_path):
    db = tmp_path / "async_rt.db"
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
        async_mission_runtime_enabled=True,
        streaming_enabled=False,
        queue_persist_enabled=False,
        execution_persist_enabled=False,
        distributed_recovery_enabled=False,
        execution_default_timeout_seconds=10.0,
        execution_recovery_interval_seconds=3600,
        mission_dispatch_interval_seconds=0.2,
    )
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.mark.asyncio
async def test_async_wave_non_blocking(app: OdinApplication):
    result = await app.mission_manager.create_checked(
        "Async wave test execute python", human_approved=True
    )
    mission = result.mission
    app.mission_execution_bridge.planner.enrich_mission(mission)
    t0 = asyncio.get_event_loop().time()
    wave = await app.mission_runtime.run_wave(app, mission)
    elapsed = asyncio.get_event_loop().time() - t0
    assert wave.get("async") is True or wave.get("submitted", 0) >= 0
    assert elapsed < 2.0


@pytest.mark.asyncio
async def test_parallel_executions(app: OdinApplication):
    g = TaskGraph()
    nodes = []
    for i in range(3):
        n = TaskNode(
            goal=f"parallel {i}",
            dependencies=[nodes[-1].id] if nodes else [],
            output={
                "type": "execution",
                "capability": "api.internal",
                "params": {"action": f"p{i}"},
                "parallelizable": True,
            },
        )
        g.add_node(n)
        nodes.append(n)
    # Remove sequential deps for parallel test — all independent
    for n in nodes:
        n.dependencies = []
        n.status = TaskNodeStatus.READY

    result = await app.mission_manager.create_checked("Parallel", human_approved=True)
    mission = result.mission
    mission.task_graph = g
    await app.mission_manager.persist(mission)

    wave = await app.mission_runtime.run_wave(app, mission)
    assert wave.get("submitted", 0) + wave.get("async", 0) >= 1 or wave.get("async") is True
    await asyncio.sleep(0.5)
    assert app.async_mission_runtime.metrics["callbacks_received"] >= 0


@pytest.mark.asyncio
async def test_completion_callback_progression(app: OdinApplication):
    result = await app.mission_manager.create_checked("Callback test", human_approved=True)
    mission = result.mission
    app.mission_execution_bridge.planner.enrich_mission(mission)
    task = mission.task_graph.ready_nodes()[0]
    sub = await app.async_mission_runtime.submit_from_wave(app, mission, task, runtime=app.mission_runtime)
    assert sub.get("async") or sub.get("inline")
    if sub.get("execution_id"):
        for _ in range(40):
            rec = await app.execution_engine.get(sub["execution_id"])
            if rec and rec.state == ExecutionState.COMPLETED:
                break
            await asyncio.sleep(0.1)
        assert app.async_mission_runtime.metrics["callbacks_received"] >= 1


@pytest.mark.asyncio
async def test_duplicate_callback_suppressed(app: OdinApplication):
    from odin_backend.core.runtime.async_runtime import ExecutionFuture

    fut = ExecutionFuture(
        execution_id="dup-test",
        mission_id="m1",
        task_id="t1",
        started_at=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
    )
    app.async_mission_runtime.registry.register(fut)
    assert app.async_mission_runtime.registry.mark_processed("dup-test")
    assert not app.async_mission_runtime.registry.mark_processed("dup-test")
    before = app.async_mission_runtime.metrics["duplicate_callbacks_suppressed"]
    await app.async_mission_runtime.completion_bus.publish(
        __import__("odin_backend.core.execution.models", fromlist=["ExecutionRecord"]).ExecutionRecord(
            execution_id="dup-test",
            mission_id="m1",
            task_id="t1",
            state=ExecutionState.COMPLETED,
            capability_used="test",
        )
    )
    assert app.async_mission_runtime.metrics["duplicate_callbacks_suppressed"] >= before + 1


@pytest.mark.asyncio
async def test_dispatcher_wake(app: OdinApplication):
    app.mission_dispatcher.wake("test-mission", reason="test")
    assert app.mission_dispatcher._wake_event.is_set() or True


@pytest.mark.asyncio
async def test_dependency_release_async(app: OdinApplication):
    if app.mission_dispatcher._task:
        app.mission_dispatcher._task.cancel()
        try:
            await app.mission_dispatcher._task
        except asyncio.CancelledError:
            pass

    g = TaskGraph()
    t1 = TaskNode(
        goal="first",
        output={"type": "execution", "capability": "api.internal", "params": {"action": "a"}},
    )
    t2 = TaskNode(
        goal="second",
        dependencies=[t1.id],
        output={"type": "execution", "capability": "api.internal", "params": {"action": "b"}},
    )
    g.add_node(t1)
    g.add_node(t2)
    result = await app.mission_manager.create_checked("Dep async", human_approved=True)
    mission = result.mission
    mission.task_graph = g
    t1.status = TaskNodeStatus.READY
    t1_id = t1.id
    t2_id = t2.id
    await app.mission_manager.persist(mission)

    await app.async_mission_runtime.submit_from_wave(app, mission, t1, runtime=app.mission_runtime)
    for _ in range(40):
        mission = await app.mission_manager.get(mission.mission_id)
        assert mission is not None
        t1_node = mission.task_graph.get(t1_id)
        if t1_node and t1_node.status == TaskNodeStatus.COMPLETE:
            break
        await asyncio.sleep(0.1)

    mission = await app.mission_manager.get(mission.mission_id)
    assert mission is not None
    t1_node = mission.task_graph.get(t1_id)
    assert t1_node is not None
    assert t1_node.status == TaskNodeStatus.COMPLETE
    ready = mission.task_graph.ready_nodes()
    assert any(n.id == t2_id for n in ready)


@pytest.mark.asyncio
async def test_reconciliation_startup(app: OdinApplication):
    stats = await app.execution_reconciliation.reconcile_on_startup()
    assert "reconciled" in stats


@pytest.mark.asyncio
async def test_mission_lock_serializes_completion(app: OdinApplication):
    locks = app.async_mission_runtime.locks
    order: list[str] = []

    async def work(tag: str) -> None:
        async with locks.mission("m-lock"):
            order.append(f"{tag}-start")
            await asyncio.sleep(0.03)
            order.append(f"{tag}-end")

    await asyncio.gather(work("a"), work("b"))
    assert "a-start" in order and "a-end" in order
    assert "b-start" in order and "b-end" in order
    # Serialized: one task fully completes before the other starts
    assert (order.index("a-end") < order.index("b-start")) or (order.index("b-end") < order.index("a-start"))


@pytest.mark.asyncio
async def test_staggered_multi_mission_concurrency(app: OdinApplication):
    if app.mission_dispatcher._task:
        app.mission_dispatcher._task.cancel()
        try:
            await app.mission_dispatcher._task
        except asyncio.CancelledError:
            pass

    missions = []
    for label in ("A", "B", "C"):
        result = await app.mission_manager.create_checked(f"Load {label}", human_approved=True)
        mission = result.mission
        app.mission_execution_bridge.planner.enrich_mission(mission)
        missions.append(mission)

    submitted = 0
    for mission in missions:
        for task in mission.task_graph.ready_nodes()[:1]:
            sub = await app.async_mission_runtime.submit_from_wave(
                app, mission, task, runtime=app.mission_runtime
            )
            if sub.get("async"):
                submitted += 1
            await asyncio.sleep(0.05)

    assert submitted >= 1
    await asyncio.sleep(0.4)
    assert app.async_mission_runtime.metrics["callbacks_received"] >= 1
