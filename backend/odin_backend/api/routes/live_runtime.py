"""Live runtime API."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/live", tags=["live-runtime"])


class CognitiveCycleRequest(BaseModel):
    objective: str


@router.get("/status")
async def live_status(request: Request) -> dict:
    app = request.app.state.odin
    state = app.kernel.get_state()
    return {
        "live_loop_enabled": app.settings.live_loop_enabled,
        "model_used": state.model_used,
        "coherence_score": state.coherence_score,
        "decision_path": state.decision_path,
        "execution_log_tail": state.execution_log[-10:],
        "reasoning_trace_tail": state.reasoning_trace[-5:],
    }


@router.post("/cognitive-cycle")
async def run_cognitive_cycle(body: CognitiveCycleRequest, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.live_loop.run_cognitive_cycle(body.objective)
    return result.model_dump(mode="json")
