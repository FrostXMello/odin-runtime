"""Agent discovery API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
async def list_agents(request: Request) -> list[dict]:
    app = request.app.state.odin
    return app.agent_registry.list_agents()
