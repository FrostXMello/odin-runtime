"""Reflection reports API."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/reflection", tags=["reflection"])


@router.get("/{workflow_id}")
async def get_reflection(workflow_id: str, request: Request) -> dict:
    app = request.app.state.odin
    report = app.reflection.get_report(workflow_id)
    if not report:
        run = app.workflow_runner.get_run(workflow_id)
        if run:
            report = await app.reflection.reflect_on_workflow(run)
        else:
            raise HTTPException(status_code=404, detail="Workflow not found")
    return report.model_dump(mode="json")
