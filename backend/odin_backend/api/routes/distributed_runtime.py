"""Distributed runtime API — queues, leases, workers, deadletters."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/runtime", tags=["distributed-runtime"])


@router.get("/leases")
async def runtime_leases(request: Request) -> dict:
    app = request.app.state.odin
    dq = app.distributed_queue
    return {
        "worker_id": dq.worker_id,
        "lease_metrics": dq.leases.metrics,
        "active": await dq.leases.list_active_leases(),
    }


@router.get("/recovery")
async def runtime_recovery(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "metrics": app.distributed_recovery.metrics,
        "distributed_recovery_enabled": app.settings.distributed_recovery_enabled,
    }


@router.post("/recovery/run")
async def runtime_recovery_run(request: Request) -> dict:
    app = request.app.state.odin
    return await app.distributed_recovery.recover_on_startup()


@router.get("/deadletters")
async def runtime_deadletters(request: Request, limit: int = 50) -> dict:
    app = request.app.state.odin
    dl = app.distributed_queue.deadletter
    if not dl:
        return {"count": 0, "items": []}
    items = await dl.list_items(limit=limit)
    return {
        "count": len(items),
        "items": [i.model_dump(mode="json") for i in items],
    }


@router.post("/deadletters/{deadletter_id}/replay")
async def runtime_deadletter_replay(deadletter_id: str, request: Request) -> dict:
    app = request.app.state.odin
    dl = app.distributed_queue.deadletter
    if not dl:
        raise HTTPException(status_code=501, detail="deadletter not enabled")
    item = await dl.replay(deadletter_id)
    if not item:
        raise HTTPException(status_code=404, detail="deadletter not found")
    if item.mission_id:
        app.mission_dispatcher.wake(item.mission_id, reason="deadletter_replay")
    return {"replayed": True, "queue_item_id": item.queue_item_id, "mission_id": item.mission_id}


@router.get("/topology")
async def runtime_topology(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_topology.snapshot()


@router.get("/routing")
async def runtime_routing(request: Request) -> dict:
    app = request.app.state.odin
    router_svc = app.capability_router
    targets = await router_svc.list_targets()
    return {
        "recent_decisions": router_svc.recent_decisions,
        "targets": [
            {
                "worker_id": t.worker_id,
                "capabilities": sorted(t.capabilities),
                "active_leases": t.active_leases,
                "concurrency": t.concurrency,
                "stale": t.stale,
                "score": t.score,
            }
            for t in targets
        ],
    }


@router.get("/pools")
async def runtime_pools(request: Request) -> dict:
    app = request.app.state.odin
    mgr = app.execution_pool_manager
    return {"pools": mgr.metrics, "default": app.settings.execution_pool_default}


@router.post("/workers/{worker_id}/drain")
async def runtime_worker_drain(worker_id: str, request: Request) -> dict:
    app = request.app.state.odin
    if worker_id == app.worker_registry.worker_id:
        await app.worker_registry.set_draining(True)
        return {"worker_id": worker_id, "draining": True}
    return {"worker_id": worker_id, "draining": False, "note": "remote drain not yet supported"}


@router.get("/workers/registry")
async def runtime_workers_registry(request: Request) -> dict:
    app = request.app.state.odin
    workers = await app.worker_registry.list_workers()
    return {"workers": workers, "local_worker_id": app.worker_registry.worker_id}
