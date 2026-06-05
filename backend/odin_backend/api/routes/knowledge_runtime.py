"""Knowledge fabric and research APIs."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["knowledge-runtime"])


class IngestFactRequest(BaseModel):
    entity: str
    fact: str
    confidence: float = 0.6
    source: str = "local"
    mission_origin: str | None = None


class ResearchStartRequest(BaseModel):
    topic: str
    mission_id: str | None = None


class ResearchTopicRequest(BaseModel):
    topic: str


class VerifySourceRequest(BaseModel):
    url: str


@router.get("/knowledge")
async def runtime_knowledge(request: Request, entity: str | None = None) -> dict:
    app = request.app.state.odin
    nodes = await app.knowledge_runtime.list_knowledge(entity=entity)
    return {"nodes": nodes, "snapshot": app.knowledge_runtime.snapshot()}


@router.post("/knowledge/ingest")
async def runtime_knowledge_ingest(body: IngestFactRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.knowledge_runtime.ingest_fact(
        entity=body.entity,
        fact=body.fact,
        confidence=body.confidence,
        source=body.source,
        mission_origin=body.mission_origin,
    )


@router.get("/research")
async def runtime_research_fabric(request: Request) -> dict:
    app = request.app.state.odin
    return app.research_fabric.snapshot()


@router.post("/research/start")
async def runtime_research_start(body: ResearchStartRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.research_fabric.start(topic=body.topic, mission_id=body.mission_id)


@router.post("/research/topic")
async def runtime_research_topic(body: ResearchTopicRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.research_fabric.research_topic(topic=body.topic)


@router.post("/research/verify")
async def runtime_research_verify(body: VerifySourceRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.research_fabric.verify_source(url=body.url)


@router.get("/world-model")
async def runtime_world_model(request: Request) -> dict:
    app = request.app.state.odin
    return app.knowledge_runtime.snapshot()["world_model"]


@router.get("/beliefs")
async def runtime_beliefs(request: Request) -> dict:
    app = request.app.state.odin
    return {"beliefs": app.knowledge_runtime.snapshot()["beliefs"]}


@router.get("/contradictions")
async def runtime_contradictions(request: Request) -> dict:
    app = request.app.state.odin
    return {"contradictions": await app.knowledge_runtime.contradictions()}


@router.get("/trends")
async def runtime_trends(request: Request, topic: str = "") -> dict:
    app = request.app.state.odin
    from odin_backend.core.research_engine.trend_analysis import analyze_trends

    hist = app.knowledge_runtime._temporal.history(topic) if topic else []
    return {"topic": topic, "trends": analyze_trends(hist)}


@router.get("/sources")
async def runtime_sources(request: Request) -> dict:
    app = request.app.state.odin
    sources = await app.knowledge_runtime._store.list_sources()
    return {"sources": sources, "web": app.web_access.snapshot(), "governance": app.research_governance.snapshot()}
