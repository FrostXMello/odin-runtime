"""Workflow run API."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("")
async def list_workflows(request: Request) -> list[dict]:
    app = request.app.state.odin
    runs = app.workflow_runner.list_runs()
    return [r.model_dump(mode="json") for r in runs]


@router.get("/{run_id}")
async def get_workflow(run_id: str, request: Request) -> dict:
    app = request.app.state.odin
    run = app.workflow_runner.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found")
    return run.model_dump(mode="json")
