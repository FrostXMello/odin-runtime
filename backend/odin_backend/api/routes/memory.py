"""Memory API — MIMIR layer."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/memory", tags=["memory"])


class MemoryStoreRequest(BaseModel):
    content: str
    category: str = "general"
    metadata: dict = Field(default_factory=dict)


class MemorySearchRequest(BaseModel):
    query: str
    limit: int = 5


@router.post("")
async def store_memory(body: MemoryStoreRequest, request: Request) -> dict:
    app = request.app.state.odin
    memory_id = await app.memory.save_memory(
        body.content, category=body.category, metadata=body.metadata
    )
    return {"memory_id": memory_id}


@router.post("/search")
async def search_memory(body: MemorySearchRequest, request: Request) -> list[dict]:
    app = request.app.state.odin
    return await app.memory.search_memory(body.query, limit=body.limit)


@router.get("/context")
async def get_context(query: str, request: Request, project: str | None = None) -> dict:
    app = request.app.state.odin
    context = await app.memory.retrieve_related_context(query, project=project)
    return {"query": query, "context": context}


@router.get("/clusters")
async def memory_clusters(request: Request) -> list[dict]:
    app = request.app.state.odin
    return await app.memory.list_clusters()


@router.get("/projects/{project}/summary")
async def project_summary(project: str, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory.summarize_project(project)
