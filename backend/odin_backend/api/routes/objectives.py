"""Objective API — reason, plan, execute workflow."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/objectives", tags=["objectives"])


class ObjectiveRequest(BaseModel):
    objective: str
    context: str = ""
    execute: bool = True
    user_confirmed: bool = False
    workflow_mode: str = "hybrid"  # sequential | parallel | hybrid


class ObjectiveResponse(BaseModel):
    plan_id: str
    objective: str
    steps: list[dict]
    run_id: str | None = None
    run_status: str | None = None


@router.post("", response_model=ObjectiveResponse)
async def submit_objective(body: ObjectiveRequest, request: Request) -> ObjectiveResponse:
    app = request.app.state.odin

    memory_context = await app.memory.retrieve_related_context(body.objective)
    full_context = f"{body.context}\n{memory_context}".strip()

    plan = await app.reasoning.reason(
        body.objective,
        context=full_context,
    )

    run_id = None
    run_status = None
    if body.execute:
        run = await app.workflow_runner.execute_plan(plan, mode=body.workflow_mode)
        run_id = run.id
        run_status = run.status.value
    return ObjectiveResponse(
        plan_id=plan.id,
        objective=plan.objective,
        steps=[s.model_dump(mode="json") for s in plan.steps],
        run_id=run_id,
        run_status=run_status,
    )
