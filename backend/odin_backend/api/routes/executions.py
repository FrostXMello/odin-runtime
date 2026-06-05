"""Real execution engine API."""

from fastapi import APIRouter, HTTPException, Request

from odin_backend.core.execution.models import ExecutionRunRequest

router = APIRouter(prefix="/executions", tags=["executions"])


def _engine(request: Request):
    return request.app.state.odin.execution_engine


@router.post("/run")
async def run_execution(body: ExecutionRunRequest, request: Request) -> dict:
    app = request.app.state.odin
    if not app.settings.execution_engine_enabled:
        raise HTTPException(503, "execution engine disabled")
    record = await app.execution_engine.submit(body)
    return record.model_dump(mode="json")


@router.get("/{execution_id}")
async def get_execution(execution_id: str, request: Request) -> dict:
    record = await _engine(request).get(execution_id)
    if not record:
        raise HTTPException(404, "execution not found")
    return record.model_dump(mode="json")


@router.get("/{execution_id}/logs")
async def get_execution_logs(execution_id: str, request: Request, tail: int = 500) -> dict:
    record = await _engine(request).get(execution_id)
    if not record:
        raise HTTPException(404, "execution not found")
    logs = await _engine(request).logs(execution_id, tail=tail)
    return {"execution_id": execution_id, **logs}


@router.post("/{execution_id}/cancel")
async def cancel_execution(execution_id: str, request: Request) -> dict:
    record = await _engine(request).cancel(execution_id)
    if not record:
        raise HTTPException(404, "execution not found")
    return record.model_dump(mode="json")


@router.post("/{execution_id}/retry")
async def retry_execution(execution_id: str, request: Request) -> dict:
    record = await _engine(request).retry(execution_id)
    if not record:
        raise HTTPException(404, "execution not found")
    return record.model_dump(mode="json")


@router.get("/{execution_id}/mission")
async def execution_mission(execution_id: str, request: Request) -> dict:
    app = request.app.state.odin
    record = await _engine(request).get(execution_id)
    if not record:
        raise HTTPException(404, "execution not found")
    mapping = app.mission_execution_bridge.get_mission_task(execution_id)
    return {
        "execution_id": execution_id,
        "mission_id": record.mission_id or (mapping[0] if mapping else None),
        "task_id": record.task_id or (mapping[1] if mapping else None),
        "state": record.state.value,
    }


@router.get("/{execution_id}/learning")
async def execution_learning(execution_id: str, request: Request) -> dict:
    app = request.app.state.odin
    record = await _engine(request).get(execution_id)
    if not record:
        raise HTTPException(404, "execution not found")
    profile = app.execution_intelligence.profiler.get(execution_id)
    cap_score = app.execution_intelligence.capability_scores().get(record.capability_used, {})
    return {
        "execution_id": execution_id,
        "capability": record.capability_used,
        "profile": profile,
        "capability_score": cap_score,
        "fingerprint_events": [
            e for e in app.experience_engine._events if e.get("execution_id") == execution_id
        ],
    }
