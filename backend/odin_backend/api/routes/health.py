"""Health and system status endpoints."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "status": "ok",
        "service": "odin-backend",
        "version": app.settings.app_version,
        "redis": app.use_redis,
    }


@router.get("/status")
async def system_status(request: Request) -> dict:
    app = request.app.state.odin
    status = await app.orchestrator.get_system_status()
    return status
