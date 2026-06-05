"""Cognitive kernel API."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

from odin_backend.core.governor.decisions import ExecutionRequest

router = APIRouter(prefix="/kernel", tags=["kernel"])


class GovernorPreviewRequest(BaseModel):
    tool_name: str
    agent_id: str = "odin"
    params: dict | None = None
    workflow_id: str | None = None
    user_confirmed: bool = False


@router.get("/state")
async def get_cognitive_state(request: Request) -> dict:
    app = request.app.state.odin
    state = app.kernel.get_state()
    return state.model_dump(mode="json")


@router.get("/explain")
async def explain_kernel(request: Request) -> dict:
    app = request.app.state.odin
    return app.kernel.explain()


@router.get("/priority")
async def get_priority_ranking(request: Request, limit: int = 10) -> dict:
    app = request.app.state.odin
    items = app.priority_engine.rank(limit)
    return {
        "items": [i.model_dump(mode="json") for i in items],
        "current_focus": app.priority_engine.top_focus(),
    }


@router.get("/graph")
async def get_context_graph(request: Request) -> dict:
    app = request.app.state.odin
    return app.context_graph.snapshot()


@router.get("/governor/decisions")
async def governor_decisions(request: Request, limit: int = 20) -> list[dict]:
    app = request.app.state.odin
    return app.governor.recent_decisions(limit)


@router.post("/governor/preview")
async def preview_governor(body: GovernorPreviewRequest, request: Request) -> dict:
    """Preview governor decision without executing tool."""
    app = request.app.state.odin
    decision = await app.governor.evaluate(
        ExecutionRequest(
            tool_name=body.tool_name,
            agent_id=body.agent_id,
            params=body.params or {},
            workflow_id=body.workflow_id,
            user_confirmed=body.user_confirmed,
        ),
        cognitive_state=app.kernel.get_state(),
    )
    return decision.model_dump()
