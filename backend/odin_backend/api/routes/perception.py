"""Perception API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/perception", tags=["perception"])


@router.get("/live")
async def perception_live(request: Request) -> dict:
    app = request.app.state.odin
    records = [p.model_dump(mode="json") for p in app.perception.live_perceptions]
    return {"count": len(records), "perceptions": records}


@router.get("/history")
async def perception_history(request: Request, limit: int = 50, mission_id: str | None = None) -> dict:
    app = request.app.state.odin
    history = app.perception_memory.history(limit=limit, mission_id=mission_id)
    return {"count": len(history), "history": history, "failure_patterns": app.perception_memory.failure_patterns()}
