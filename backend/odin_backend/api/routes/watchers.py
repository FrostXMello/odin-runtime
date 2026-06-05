"""Watcher insights API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/watchers", tags=["watchers"])


@router.get("/insights/recent")
async def recent_insights(request: Request, limit: int = 50) -> list[dict]:
    app = request.app.state.odin
    events = app.event_hub.recent(limit)
    return [e for e in events if e.get("type") in ("watcher.insight", "recommendation.created")]
