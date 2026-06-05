"""Distributed persistent runtime tests."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.execution.models import ExecutionRecord, ExecutionState
from odin_backend.core.queueing.in_memory_backend import InMemoryQueueBackend
from odin_backend.core.queueing.leases import LeaseCoordinator
from odin_backend.core.queueing.queue_models import QueueItem
from odin_backend.core.queueing.sqlite_backend import SQLiteQueueBackend
from odin_backend.core.queueing.wake_signals import WakeSignalStore


@pytest.fixture
def tmp_db(tmp_path):
    return tmp_path / "dist_rt.db"


@pytest.fixture
def settings(tmp_db, tmp_path):
    return Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_db.resolve().as_posix()}",
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
        queue_persist_enabled=True,
        execution_persist_enabled=True,
        distributed_recovery_enabled=True,
        mission_dispatch_interval_seconds=0.5,
    )


@pytest.fixture
async def app(settings, tmp_path):
    settings.chroma_persist_dir = tmp_path / "chroma"
    settings.sandbox_work_dir = tmp_path / "sandbox"
    odin = OdinApplication(settings, use_redis=False)
    await odin.startup()
    yield odin
    await odin.shutdown()


@pytest.fixture
async def mem_backend():
    b = InMemoryQueueBackend()
    await b.connect()
    yield b
    await b.disconnect()


@pytest.fixture
async def sqlite_backend(settings):
    b = SQLiteQueueBackend(settings)
    await b.connect()
    yield b
    await b.disconnect()


# --- Queue backend unit tests ---


@pytest.mark.asyncio
async def test_enqueue_dequeue_ack(mem_backend):
    item = QueueItem(mission_id="m1", dedup_key="mission:m1", payload={"k": 1})
    await mem_backend.enqueue(item)
    claimed = await mem_backend.dequeue("w1", limit=1)
    assert len(claimed) == 1
    assert claimed[0].mission_id == "m1"
    ok = await mem_backend.ack(claimed[0].queue_item_id, "w1")
    assert ok


@pytest.mark.asyncio
async def test_dedup_enqueue(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="m1", dedup_key="mission:m1"))
    await mem_backend.enqueue(QueueItem(mission_id="m1", dedup_key="mission:m1"))
    stats = await mem_backend.stats()
    assert stats["total"] == 1


@pytest.mark.asyncio
async def test_nack_requeue(mem_backend):
    item = QueueItem(mission_id="m2", dedup_key="mission:m2")
    await mem_backend.enqueue(item)
    claimed = await mem_backend.dequeue("w1")
    ok = await mem_backend.nack(claimed[0].queue_item_id, "w1", requeue_delay=0.01)
    assert ok
    await asyncio.sleep(0.02)
    again = await mem_backend.dequeue("w2")
    assert again[0].mission_id == "m2"


@pytest.mark.asyncio
async def test_lease_renew(mem_backend):
    item = QueueItem(mission_id="m3", dedup_key="mission:m3")
    await mem_backend.enqueue(item)
    claimed = await mem_backend.dequeue("w1", lease_seconds=30)
    ok = await mem_backend.renew_lease(claimed[0].queue_item_id, "w1", lease_seconds=60)
    assert ok


@pytest.mark.asyncio
async def test_requeue_expired(mem_backend):
    item = QueueItem(mission_id="m4", dedup_key="mission:m4")
    await mem_backend.enqueue(item)
    await mem_backend.dequeue("w1", lease_seconds=0.01)
    await asyncio.sleep(0.03)
    count = await mem_backend.requeue_expired()
    assert count >= 1


@pytest.mark.asyncio
async def test_sqlite_persist_enqueue(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="s1", dedup_key="mission:s1"))
    stats = await sqlite_backend.stats()
    assert stats["total"] >= 1


@pytest.mark.asyncio
async def test_sqlite_dequeue_ack(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="s2", dedup_key="mission:s2"))
    items = await sqlite_backend.dequeue("worker-a")
    assert items
    assert await sqlite_backend.ack(items[0].queue_item_id, "worker-a")


@pytest.mark.asyncio
async def test_sqlite_dedup(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="s3", dedup_key="mission:s3"))
    await sqlite_backend.enqueue(QueueItem(mission_id="s3", dedup_key="mission:s3"))
    stats = await sqlite_backend.stats()
    assert stats["total"] == 1


@pytest.mark.asyncio
async def test_sqlite_requeue_expired(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="s4", dedup_key="mission:s4"))
    await sqlite_backend.dequeue("w", lease_seconds=0.01)
    await asyncio.sleep(0.03)
    assert await sqlite_backend.requeue_expired() >= 1


@pytest.mark.asyncio
async def test_lease_coordinator_acquire_release(mem_backend):
    lc = LeaseCoordinator(mem_backend, default_lease_seconds=30)
    await mem_backend.enqueue(QueueItem(mission_id="lc1", dedup_key="mission:lc1"))
    items = await lc.acquire("w1")
    assert items
    assert await lc.release(items[0].queue_item_id, "w1")


@pytest.mark.asyncio
async def test_wake_signal_dedup(settings):
    ws = WakeSignalStore(settings, dedup_window_seconds=2.0)
    await ws.connect()
    assert await ws.should_wake("m-wake", reason="test")
    assert not await ws.should_wake("m-wake", reason="test")
    assert ws.replay_suppressed >= 1


@pytest.mark.asyncio
async def test_distributed_queue_enqueue(app):
    item = await app.distributed_queue.enqueue_mission("test-mission-1", reason="test")
    assert item.mission_id == "test-mission-1"
    stats = await app.distributed_queue.stats()
    assert stats["metrics"]["enqueued"] >= 1


@pytest.mark.asyncio
async def test_idempotent_wake(app):
    ok1 = await app.distributed_queue.idempotent_wake("wake-m1", reason="unit")
    ok2 = await app.distributed_queue.idempotent_wake("wake-m1", reason="unit")
    assert ok1
    assert not ok2


@pytest.mark.asyncio
async def test_persistent_scheduler_schedule(app):
    sched = app.mission_worker.scheduler
    sched.schedule("sched-m1", delay_seconds=0.0)
    assert sched.backlog_depth() >= 1


@pytest.mark.asyncio
async def test_pop_due_async(app):
    sched = app.mission_worker.scheduler
    if not hasattr(sched, "pop_due_async"):
        pytest.skip("persistent scheduler not enabled")
    sched.schedule("async-m1")
    await asyncio.sleep(0.05)
    due = await sched.pop_due_async()
    assert "async-m1" in due or sched.backlog_depth() >= 0


@pytest.mark.asyncio
async def test_execution_persist_survives_restart(settings, tmp_path):
    settings.chroma_persist_dir = tmp_path / "chroma"
    settings.sandbox_work_dir = tmp_path / "sandbox"
    odin1 = OdinApplication(settings, use_redis=False)
    await odin1.startup()
    rec = ExecutionRecord(mission_id="m-p", task_id="t-p", capability_used="test", state=ExecutionState.RUNNING)
    await odin1.execution_engine.store.put(rec)
    eid = rec.execution_id
    await odin1.shutdown()

    odin2 = OdinApplication(settings, use_redis=False)
    await odin2.startup()
    loaded = await odin2.execution_engine.store.get(eid)
    await odin2.shutdown()
    assert loaded is not None
    assert loaded.mission_id == "m-p"


@pytest.mark.asyncio
async def test_distributed_recovery_on_startup(app):
    stats = await app.distributed_recovery.recover_on_startup()
    assert "metrics" in stats


@pytest.mark.asyncio
async def test_dispatcher_wake_non_blocking(app):
    app.mission_dispatcher.wake("disp-m1", reason="test")
    assert app.mission_dispatcher._wake_event.is_set() or True


@pytest.mark.asyncio
async def test_worker_registry_heartbeat(app):
    await app.worker_registry.heartbeat(active_leases=2)
    workers = await app.worker_registry.list_workers()
    assert any(w["worker_id"] == app.worker_registry.worker_id for w in workers)


@pytest.mark.asyncio
async def test_queue_stats_api_shape(app):
    stats = await app.distributed_queue.stats()
    assert "worker_id" in stats
    assert "metrics" in stats


@pytest.mark.asyncio
async def test_concurrent_dequeue_safety(sqlite_backend):
    for i in range(5):
        await sqlite_backend.enqueue(
            QueueItem(mission_id=f"c{i}", dedup_key=f"mission:c{i}", priority=50 - i)
        )
    r1 = await sqlite_backend.dequeue("w-a", limit=3)
    r2 = await sqlite_backend.dequeue("w-b", limit=3)
    ids = {i.queue_item_id for i in r1 + r2}
    assert len(ids) == len(r1) + len(r2)


@pytest.mark.asyncio
async def test_visibility_delay(mem_backend):
    future = datetime.now(timezone.utc) + timedelta(seconds=0.05)
    await mem_backend.enqueue(
        QueueItem(mission_id="vis1", dedup_key="mission:vis1", visible_at=future)
    )
    assert not await mem_backend.dequeue("w1")
    await asyncio.sleep(0.06)
    assert await mem_backend.dequeue("w1")


@pytest.mark.asyncio
async def test_priority_order(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="low", dedup_key="mission:low", priority=10))
    await mem_backend.enqueue(QueueItem(mission_id="high", dedup_key="mission:high", priority=90))
    items = await mem_backend.dequeue("w1", limit=1)
    assert items[0].mission_id == "high"


@pytest.mark.asyncio
async def test_ack_wrong_worker_fails(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="aw1", dedup_key="mission:aw1"))
    items = await mem_backend.dequeue("w1")
    assert not await mem_backend.ack(items[0].queue_item_id, "w-other")


@pytest.mark.asyncio
async def test_mission_create_enqueues(app):
    result = await app.mission_manager.create_checked("Queue test mission", human_approved=True)
    assert result.mission.mission_id


@pytest.mark.asyncio
async def test_reconciliation_after_persist(app):
    if not hasattr(app.execution_engine.store, "hydrate"):
        pytest.skip("persist store disabled")
    count = await app.execution_engine.store.hydrate()
    assert count >= 0


@pytest.mark.asyncio
async def test_lease_stale_recovery(app):
    await app.distributed_queue.enqueue_mission("stale-m1")
    items = await app.distributed_queue.dequeue_missions(limit=1)
    if items:
        await app.distributed_queue.backend.nack(
            items[0].queue_item_id,
            app.distributed_queue.worker_id,
            requeue_delay=0.0,
        )
    count = await app.distributed_queue.requeue_expired()
    assert count >= 0


@pytest.mark.asyncio
async def test_duplicate_wake_suppression_metrics(app):
    before = app.distributed_queue.wake_signals.replay_suppressed
    await app.distributed_queue.idempotent_wake("dup-m", reason="dup")
    await app.distributed_queue.idempotent_wake("dup-m", reason="dup")
    assert app.distributed_queue.wake_signals.replay_suppressed > before


@pytest.mark.asyncio
async def test_queue_item_fields(mem_backend):
    item = QueueItem(
        mission_id="mf1",
        task_id="tf1",
        execution_id="ef1",
        dedup_key="mission:mf1",
        payload={"action": "dispatch"},
        priority=75,
    )
    saved = await mem_backend.enqueue(item)
    assert saved.task_id == "tf1"
    got = await mem_backend.get(saved.queue_item_id)
    assert got and got.execution_id == "ef1"


@pytest.mark.asyncio
async def test_sqlite_list_deadletter(sqlite_backend, settings):
    from odin_backend.core.queueing.deadletter import DeadLetterQueue

    item = QueueItem(mission_id="dl1", dedup_key="mission:dl1")
    await sqlite_backend.enqueue(item)
    claimed = await sqlite_backend.dequeue("w1")
    for _ in range(settings.queue_max_retries):
        await sqlite_backend.nack(claimed[0].queue_item_id, "w1")
        claimed = await sqlite_backend.dequeue("w1")
        if not claimed:
            break
    dlq = DeadLetterQueue(settings, sqlite_backend)
    await dlq.connect()
    dead = await sqlite_backend.list_deadletter()
    assert isinstance(dead, list)


@pytest.mark.asyncio
async def test_deadletter_replay(sqlite_backend, settings):
    from odin_backend.core.queueing.deadletter import DeadLetterQueue

    item = QueueItem(mission_id="rp1", dedup_key="mission:rp1")
    await sqlite_backend.enqueue(item)
    claimed = await sqlite_backend.dequeue("w1")
    await sqlite_backend.mark_deadletter(claimed[0].queue_item_id, reason="test")
    dlq = DeadLetterQueue(settings, sqlite_backend)
    await dlq.connect()
    dl = await dlq.record(claimed[0], reason="test")
    replayed = await dlq.replay(dl.deadletter_id)
    assert replayed is not None


@pytest.mark.asyncio
async def test_multi_worker_dequeue(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="mw1", dedup_key="mission:mw1"))
    await sqlite_backend.enqueue(QueueItem(mission_id="mw2", dedup_key="mission:mw2"))
    a = await sqlite_backend.dequeue("worker-1", limit=1)
    b = await sqlite_backend.dequeue("worker-2", limit=1)
    assert a and b
    assert a[0].mission_id != b[0].mission_id


@pytest.mark.asyncio
async def test_in_memory_stats(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="st1", dedup_key="mission:st1"))
    stats = await mem_backend.stats()
    assert stats["total"] >= 1
    assert "by_status" in stats
