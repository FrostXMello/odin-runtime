"""Cognition stream API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/cognition", tags=["cognition"])


@router.get("/recent")
async def recent_cognition(request: Request, limit: int = 100) -> list[dict]:
    app = request.app.state.odin
    return app.cognition.recent(limit)
