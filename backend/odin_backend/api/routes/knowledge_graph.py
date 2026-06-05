"""Knowledge graph API."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/knowledge-graph", tags=["knowledge-graph"])


@router.get("/search")
async def graph_search(q: str, request: Request, limit: int = 10) -> list[dict]:
    app = request.app.state.odin
    return app.knowledge_graph.contextual_graph_search(q, limit)


@router.get("/related/{entity_id}")
async def related_entities(entity_id: str, request: Request) -> list[dict]:
    app = request.app.state.odin
    return app.knowledge_graph.find_related_entities(entity_id)


@router.get("/project/{project_id}/dependencies")
async def project_map(project_id: str, request: Request) -> dict:
    app = request.app.state.odin
    return app.knowledge_graph.project_dependency_map(project_id)
