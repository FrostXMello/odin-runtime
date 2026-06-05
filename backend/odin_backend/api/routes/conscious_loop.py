"""Runtime conscious loop API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/conscious-loop", tags=["conscious-loop"])


@router.get("/status")
async def loop_status(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "enabled": app.settings.conscious_loop_enabled,
        "tick_count": app.conscious_loop.tick_count,
        "last_cycle": app.conscious_loop.last_cycle(),
        "pending_escalations": app.conscious_loop.pending_escalations(),
        "autonomy_level": app.autonomy.current_level,
    }


@router.post("/tick")
async def manual_tick(request: Request) -> dict:
    """Run a single conscious cycle (for debugging)."""
    app = request.app.state.odin
    result = await app.conscious_loop.run_cycle()
    return result.model_dump(mode="json")


@router.get("/escalations")
async def list_escalations(request: Request) -> list[dict]:
    app = request.app.state.odin
    return app.conscious_loop.pending_escalations()
