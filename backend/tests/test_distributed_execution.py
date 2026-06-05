"""Distributed execution fabric tests — multi-node routing, fencing, pools."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from odin_backend.config import Settings
from odin_backend.core.app import OdinApplication
from odin_backend.core.distributed.routing import CapabilityRouter, DEFAULT_CAPABILITIES
from odin_backend.core.distributed.topology import RuntimeTopology
from odin_backend.core.distributed.transport import create_queue_backend
from odin_backend.core.execution.adapters.executor_adapter import (
    LocalSubprocessAdapter,
    get_executor_adapter,
)
from odin_backend.core.execution.leases import LeaseManager
from odin_backend.core.execution.models import ExecutionRecord, ExecutionRunRequest, ExecutionState
from odin_backend.core.execution.pools.pool_manager import ExecutionPool, ExecutionPoolManager
from odin_backend.core.queueing.in_memory_backend import InMemoryQueueBackend
from odin_backend.core.queueing.leases import LeaseCoordinator
from odin_backend.core.queueing.queue_models import QueueItem
from odin_backend.core.queueing.recovery import DistributedRecoveryCoordinator
from odin_backend.core.queueing.sqlite_backend import SQLiteQueueBackend
from odin_backend.core.runtime.workers import WorkerRegistry, new_worker_id
from odin_backend.runtime_worker.execution_worker import ExecutionWorker
from odin_backend.runtime_worker.registration import WorkerRegistration


@pytest.fixture
def tmp_db(tmp_path):
    return tmp_path / "dist_exec.db"


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
        queue_backend="sqlite",
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


# --- Fencing ---


@pytest.mark.asyncio
async def test_dequeue_assigns_fencing_token(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="f1", dedup_key="mission:f1"))
    items = await mem_backend.dequeue("w1")
    assert items[0].fencing_token is not None
    assert items[0].fencing_token >= 1


@pytest.mark.asyncio
async def test_fencing_token_monotonic(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="f2a", dedup_key="mission:f2a"))
    await mem_backend.enqueue(QueueItem(mission_id="f2b", dedup_key="mission:f2b"))
    a = await mem_backend.dequeue("w1", limit=1)
    await mem_backend.ack(a[0].queue_item_id, "w1", fencing_token=a[0].fencing_token)
    b = await mem_backend.dequeue("w1", limit=1)
    assert b[0].fencing_token > a[0].fencing_token


@pytest.mark.asyncio
async def test_ack_stale_fence_rejected(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="f3", dedup_key="mission:f3"))
    items = await mem_backend.dequeue("w1", lease_seconds=0.01)
    token = items[0].fencing_token
    await asyncio.sleep(0.03)
    await mem_backend.requeue_expired()
    again = await mem_backend.dequeue("w2")
    assert again and again[0].fencing_token != token
    assert not await mem_backend.ack(items[0].queue_item_id, "w1", fencing_token=token)


@pytest.mark.asyncio
async def test_ack_valid_fence(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="f4", dedup_key="mission:f4"))
    items = await mem_backend.dequeue("w1")
    assert await mem_backend.ack(items[0].queue_item_id, "w1", fencing_token=items[0].fencing_token)


@pytest.mark.asyncio
async def test_renew_stale_fence(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="f5", dedup_key="mission:f5"))
    items = await mem_backend.dequeue("w1", lease_seconds=0.01)
    token = items[0].fencing_token
    await asyncio.sleep(0.03)
    await mem_backend.requeue_expired()
    await mem_backend.dequeue("w2")
    assert not await mem_backend.renew_lease(
        items[0].queue_item_id, "w1", lease_seconds=30, fencing_token=token
    )


@pytest.mark.asyncio
async def test_nack_stale_fence(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="f6", dedup_key="mission:f6"))
    items = await mem_backend.dequeue("w1", lease_seconds=0.01)
    token = items[0].fencing_token
    await asyncio.sleep(0.03)
    await mem_backend.requeue_expired()
    await mem_backend.dequeue("w2")
    assert not await mem_backend.nack(
        items[0].queue_item_id, "w1", fencing_token=token
    )


@pytest.mark.asyncio
async def test_sqlite_fencing_token(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="sf1", dedup_key="mission:sf1"))
    items = await sqlite_backend.dequeue("w1")
    assert items[0].fencing_token is not None


@pytest.mark.asyncio
async def test_sqlite_fence_ack(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="sf2", dedup_key="mission:sf2"))
    items = await sqlite_backend.dequeue("w1")
    assert await sqlite_backend.ack(
        items[0].queue_item_id, "w1", fencing_token=items[0].fencing_token
    )


@pytest.mark.asyncio
async def test_lease_coordinator_tracks_fence(mem_backend):
    lc = LeaseCoordinator(mem_backend)
    await mem_backend.enqueue(QueueItem(mission_id="lc-f", dedup_key="mission:lc-f"))
    items = await lc.acquire("w1")
    assert lc.fencing_token_for(items[0].queue_item_id) == items[0].fencing_token
    assert await lc.release(items[0].queue_item_id, "w1")
    assert lc.fencing_token_for(items[0].queue_item_id) is None


@pytest.mark.asyncio
async def test_lease_coordinator_fence_reject_metrics(mem_backend):
    lc = LeaseCoordinator(mem_backend)
    await mem_backend.enqueue(QueueItem(mission_id="lc-r", dedup_key="mission:lc-r"))
    items = await lc.acquire("w1")
    token = items[0].fencing_token
    await mem_backend.nack(items[0].queue_item_id, "w1", fencing_token=token)
    await lc.acquire("w2")
    assert not await lc.release(items[0].queue_item_id, "w1", fencing_token=token)
    assert lc.metrics["fence_rejected"] >= 1


@pytest.mark.asyncio
async def test_execution_lease_fence():
    lm = LeaseManager()
    rec = ExecutionRecord(capability_used="python.safe")
    lm.acquire(rec)
    assert rec.fencing_token is not None
    assert lm.validate_fence(rec)
    assert lm.validate_fence(rec, rec.fencing_token)
    assert not lm.validate_fence(rec, rec.fencing_token + 999)


@pytest.mark.asyncio
async def test_execution_fence_release():
    lm = LeaseManager()
    rec = ExecutionRecord(capability_used="shell.safe")
    lm.acquire(rec)
    fence = rec.fencing_token
    lm.release(rec.execution_id)
    assert not lm.validate_fence(rec, fence)


# --- Capability routing ---


@pytest.mark.asyncio
async def test_capability_router_matches_exact(app):
    router = CapabilityRouter(app)
    target = await router.route("python.safe")
    assert target is not None


@pytest.mark.asyncio
async def test_capability_router_prefix_wildcard():
    router = CapabilityRouter(None)
    assert router._matches("api.external", {"api.*"})


@pytest.mark.asyncio
async def test_capability_router_stale_penalty():
    router = CapabilityRouter(None)
    t = type("T", (), {"stale": True, "capabilities": DEFAULT_CAPABILITIES, "active_leases": 0, "concurrency": 4})()
    assert router._score(t, "python.safe") < 0


@pytest.mark.asyncio
async def test_capability_router_prefers_low_load():
    router = CapabilityRouter(None)
    from odin_backend.core.distributed.routing import WorkerRouteTarget

    a = WorkerRouteTarget("a", capabilities=set(DEFAULT_CAPABILITIES), active_leases=0, concurrency=4)
    b = WorkerRouteTarget("b", capabilities=set(DEFAULT_CAPABILITIES), active_leases=3, concurrency=4)
    assert router._score(a, "python.safe") > router._score(b, "python.safe")


@pytest.mark.asyncio
async def test_capability_router_decisions(app):
    router = app.capability_router
    await router.route("workflow.execute")
    assert len(router.recent_decisions) >= 1


@pytest.mark.asyncio
async def test_capability_router_no_match():
    router = CapabilityRouter(None)
    from odin_backend.core.distributed.routing import WorkerRouteTarget

    t = WorkerRouteTarget("x", capabilities={"browser.*"}, active_leases=0, concurrency=4)
    assert router._score(t, "python.safe") < 0


# --- Execution pools ---


@pytest.mark.asyncio
async def test_execution_pool_run():
    pool = ExecutionPool("test", max_concurrent=2)
    result = await pool.run(lambda: asyncio.sleep(0))
    assert result is None
    assert pool.metrics.completed >= 1


@pytest.mark.asyncio
async def test_execution_pool_rejects_at_capacity():
    pool = ExecutionPool("full", max_concurrent=1)
    gate = asyncio.Event()

    async def block():
        await gate.wait()

    t = asyncio.create_task(pool.run(block))
    await asyncio.sleep(0.01)
    with pytest.raises(RuntimeError):
        await pool.run(lambda: asyncio.sleep(0))
    gate.set()
    await t


@pytest.mark.asyncio
async def test_pool_manager_route_shell(app):
    mgr = app.execution_pool_manager
    pool = mgr.route_pool("shell.safe")
    assert pool.name == "subprocess"


@pytest.mark.asyncio
async def test_pool_manager_route_python(app):
    mgr = app.execution_pool_manager
    pool = mgr.route_pool("python.safe")
    assert pool.name == "local"


@pytest.mark.asyncio
async def test_pool_manager_metrics(app):
    metrics = app.execution_pool_manager.metrics
    assert "local" in metrics
    assert "subprocess" in metrics


# --- Topology ---


@pytest.mark.asyncio
async def test_topology_snapshot(app):
    snap = await app.runtime_topology.snapshot()
    assert "nodes" in snap
    assert "edges" in snap
    assert snap["transport"] == "sqlite"


@pytest.mark.asyncio
async def test_topology_has_queue_node(app):
    snap = await app.runtime_topology.snapshot()
    kinds = {n["kind"] for n in snap["nodes"]}
    assert "queue" in kinds


@pytest.mark.asyncio
async def test_topology_has_control_plane(app):
    snap = await app.runtime_topology.snapshot()
    ids = {n["node_id"] for n in snap["nodes"]}
    assert "control-plane" in ids


# --- Worker registry ---


@pytest.mark.asyncio
async def test_worker_capabilities_from_settings(settings):
    settings.worker_capabilities = "python.safe,browser.*"
    reg = WorkerRegistry(settings, new_worker_id())
    assert "python.safe" in reg.capabilities


@pytest.mark.asyncio
async def test_worker_drain(app):
    await app.worker_registry.set_draining(True)
    workers = await app.worker_registry.list_workers()
    local = next(w for w in workers if w["worker_id"] == app.worker_registry.worker_id)
    assert local.get("draining") is True


@pytest.mark.asyncio
async def test_new_worker_id_unique():
    assert new_worker_id() != new_worker_id()


@pytest.mark.asyncio
async def test_worker_registration(app):
    reg = WorkerRegistration(app)
    await reg.register(role="execution", capabilities=["python.safe"])
    assert "python.safe" in app.worker_registry.capabilities


# --- Recovery ---


@pytest.mark.asyncio
async def test_recovery_abandoned_leases(app):
    count = await app.distributed_recovery.recover_abandoned_leases()
    assert count >= 0


@pytest.mark.asyncio
async def test_recovery_topology_metrics(app):
    stats = await app.distributed_recovery.recover_on_startup()
    assert "topology" in stats or "metrics" in stats


@pytest.mark.asyncio
async def test_recovery_coordinator_metrics(app):
    assert "leases_recovered" in app.distributed_recovery.metrics


# --- Adapters ---


@pytest.mark.asyncio
async def test_local_subprocess_adapter():
    adapter = LocalSubprocessAdapter()
    health = await adapter.health()
    assert health["status"] == "healthy"
    started = await adapter.start(execution_id="e1", spec={})
    assert started["started"]


@pytest.mark.asyncio
async def test_get_executor_adapter_default():
    adapter = get_executor_adapter("local")
    assert isinstance(adapter, LocalSubprocessAdapter)


# --- Transport factory ---


@pytest.mark.asyncio
async def test_create_queue_backend_sqlite(settings):
    settings.queue_backend = "sqlite"
    backend = create_queue_backend(settings)
    await backend.connect()
    assert isinstance(backend, SQLiteQueueBackend)
    await backend.disconnect()


@pytest.mark.asyncio
async def test_create_queue_backend_memory(settings):
    settings.queue_backend = "memory"
    backend = create_queue_backend(settings)
    await backend.connect()
    assert isinstance(backend, InMemoryQueueBackend)
    await backend.disconnect()


# --- Distributed queue with fencing ---


@pytest.mark.asyncio
async def test_distributed_queue_dequeue_has_fence(app):
    await app.distributed_queue.enqueue_mission("fence-m1")
    items = await app.distributed_queue.dequeue_missions(limit=1)
    if items:
        assert items[0].fencing_token is not None


@pytest.mark.asyncio
async def test_duplicate_execution_prevention_fence(mem_backend):
    lc = LeaseCoordinator(mem_backend)
    await mem_backend.enqueue(QueueItem(mission_id="dup", dedup_key="mission:dup"))
    first = await lc.acquire("w1")
    token = first[0].fencing_token
    await mem_backend.nack(first[0].queue_item_id, "w1", fencing_token=token)
    await lc.acquire("w2")
    assert not await lc.release(first[0].queue_item_id, "w1", fencing_token=token)


# --- Execution engine pool integration ---


@pytest.mark.asyncio
async def test_execution_submit_assigns_pool(app):
    req = ExecutionRunRequest(capability="python.safe", mission_id="m-pool")
    rec = await app.execution_engine.submit(req)
    assert rec.pool_name == "local"


@pytest.mark.asyncio
async def test_execution_submit_shell_pool(app):
    req = ExecutionRunRequest(capability="shell.safe", mission_id="m-sh")
    rec = await app.execution_engine.submit(req)
    assert rec.pool_name == "subprocess"


# --- API shape (via app components) ---


@pytest.mark.asyncio
async def test_routing_api_shape(app):
    targets = await app.capability_router.list_targets()
    assert isinstance(targets, list)


@pytest.mark.asyncio
async def test_pools_api_shape(app):
    metrics = app.execution_pool_manager.metrics
    assert "local" in metrics


# --- Reconnect / replay ---


@pytest.mark.asyncio
async def test_requeue_clears_fence(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="rq1", dedup_key="mission:rq1"))
    items = await mem_backend.dequeue("w1", lease_seconds=0.01)
    await asyncio.sleep(0.03)
    await mem_backend.requeue_expired()
    again = await mem_backend.dequeue("w2")
    assert again[0].fencing_token != items[0].fencing_token


@pytest.mark.asyncio
async def test_sqlite_reconnect_dequeue(sqlite_backend):
    await sqlite_backend.enqueue(QueueItem(mission_id="rc1", dedup_key="mission:rc1"))
    await sqlite_backend.disconnect()
    await sqlite_backend.connect()
    items = await sqlite_backend.dequeue("w1")
    assert items


# --- Worker process components ---


@pytest.mark.asyncio
async def test_execution_worker_instantiation(app):
    worker = ExecutionWorker(app)
    assert worker is not None


@pytest.mark.asyncio
async def test_lease_epoch_increments(mem_backend):
    await mem_backend.enqueue(QueueItem(mission_id="ep1", dedup_key="mission:ep1"))
    a = await mem_backend.dequeue("w1")
    await mem_backend.ack(a[0].queue_item_id, "w1", fencing_token=a[0].fencing_token)
    await mem_backend.enqueue(QueueItem(mission_id="ep2", dedup_key="mission:ep2"))
    b = await mem_backend.dequeue("w1")
    assert b[0].lease_epoch >= a[0].lease_epoch


@pytest.mark.asyncio
async def test_required_capability_field(mem_backend):
    item = QueueItem(mission_id="cap1", dedup_key="mission:cap1", required_capability="python.safe")
    saved = await mem_backend.enqueue(item)
    assert saved.required_capability == "python.safe"


@pytest.mark.asyncio
async def test_topology_routing_decisions(app):
    await app.capability_router.route("filesystem.read")
    snap = await app.runtime_topology.snapshot()
    assert "routing_decisions" in snap


@pytest.mark.asyncio
async def test_app_has_distributed_components(app):
    assert hasattr(app, "capability_router")
    assert hasattr(app, "runtime_topology")
    assert hasattr(app, "execution_pool_manager")
    assert hasattr(app, "distributed_pubsub")
