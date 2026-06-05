"""Browser intelligence API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/browser", tags=["browser"])


@router.get("/tabs")
async def active_tabs(request: Request) -> list[dict]:
    app = request.app.state.odin
    return await app.browser.get_active_tabs()


@router.get("/session")
async def session_analysis(request: Request) -> dict:
    app = request.app.state.odin
    session = await app.browser.analyze_session()
    return session.model_dump(mode="json")


@router.get("/research-cluster")
async def research_cluster(request: Request) -> dict:
    app = request.app.state.odin
    return await app.browser.detect_research_cluster()
