"""Task management API."""

from fastapi import APIRouter, HTTPException, Request

from odin_backend.models.task import Task, TaskCreate, TaskStatus

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("")
async def list_tasks(
    request: Request,
    status: TaskStatus | None = None,
    limit: int = 50,
) -> list[Task]:
    app = request.app.state.odin
    return await app.task_queue.list_tasks(status=status, limit=limit)


@router.post("", response_model=Task)
async def create_task(create: TaskCreate, request: Request) -> Task:
    app = request.app.state.odin
    return await app.orchestrator.submit_task(create)


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str, request: Request) -> Task:
    app = request.app.state.odin
    task = await app.orchestrator.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{task_id}/timeline")
async def task_timeline(task_id: str, request: Request) -> dict:
    """Resolve mission graph task by id across active missions."""
    app = request.app.state.odin
    from odin_backend.core.observability.timeline import build_task_timeline

    for mission in await app.mission_manager.list_active_missions():
        if mission.task_graph.get(task_id):
            events = app.observability.tracer.store.get_task_events(task_id)
            return build_task_timeline(mission, task_id, events)
    for mission in await app.mission_manager.list_missions(limit=100):
        if mission.task_graph.get(task_id):
            events = app.observability.tracer.store.get_task_events(task_id)
            return build_task_timeline(mission, task_id, events)
    raise HTTPException(status_code=404, detail="Task not found in mission graph")


@router.delete("/{task_id}", response_model=Task)
async def cancel_task(task_id: str, request: Request) -> Task:
    app = request.app.state.odin
    task = await app.orchestrator.cancel_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
