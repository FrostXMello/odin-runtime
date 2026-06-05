"""Runtime health and agent registry API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/runtime", tags=["runtime"])


@router.get("/status")
async def runtime_status(request: Request) -> dict:
    app = request.app.state.odin
    return app.runtime.get_status()


@router.get("/agents")
async def runtime_agents(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [r.model_dump(mode="json") for r in app.runtime.registry.list_all()]
