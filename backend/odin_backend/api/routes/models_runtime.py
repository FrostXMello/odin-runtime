"""Local model cognitive runtime APIs."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["models-runtime"])


class LoadModelRequest(BaseModel):
    model: str


class ReasoningRunRequest(BaseModel):
    objective: str
    mission_id: str | None = None


class ReflectionRunRequest(BaseModel):
    plan: str
    objective: str
    mission_id: str | None = None


@router.get("/models")
async def runtime_models(request: Request) -> dict:
    app = request.app.state.odin
    available = await app.model_manager.list_available()
    return {
        "registry": app.model_registry.snapshot(),
        "available": available,
        "provider": app.model_registry.provider.name,
    }


@router.get("/models/loaded")
async def runtime_models_loaded(request: Request) -> dict:
    app = request.app.state.odin
    loaded = [p.model_dump(mode="json") for p in app.model_registry.loaded_models()]
    return {"loaded": loaded}


@router.post("/models/load")
async def runtime_models_load(body: LoadModelRequest, request: Request) -> dict:
    app = request.app.state.odin
    result = await app.model_resource_scheduler.load_with_budget(body.model)
    return result


@router.post("/models/unload")
async def runtime_models_unload(body: LoadModelRequest, request: Request) -> dict:
    app = request.app.state.odin
    ok = await app.model_manager.unload(body.model)
    return {"model": body.model, "unloaded": ok}


@router.get("/agents")
async def runtime_agents(request: Request) -> dict:
    app = request.app.state.odin
    society = await app.agent_society.list_agents() if hasattr(app, "agent_society") else []
    return {
        "agents": app.cognitive_agents.list_agents(),
        "society_agents": society,
    }


@router.get("/reasoning")
async def runtime_reasoning(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "pipeline": "memory-grounded",
        "runtime_metrics": app.model_manager.runtime.metrics,
        "embedding_metrics": app.embedding_runtime.metrics,
    }


@router.post("/reasoning/run")
async def runtime_reasoning_run(body: ReasoningRunRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.reasoning_pipeline.run(objective=body.objective, mission_id=body.mission_id)


@router.get("/reflection")
async def runtime_reflection(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "max_depth": app.settings.reflection_max_depth,
        "time_budget_seconds": app.settings.reflection_time_budget_seconds,
    }


@router.post("/reflection/run")
async def runtime_reflection_run(body: ReflectionRunRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_reflection.reflect(
        plan=body.plan,
        objective=body.objective,
        mission_id=body.mission_id,
    )


@router.get("/embeddings")
async def runtime_embeddings(request: Request) -> dict:
    app = request.app.state.odin
    return app.embedding_runtime.snapshot()


@router.get("/resources")
async def runtime_resources(request: Request) -> dict:
    app = request.app.state.odin
    return app.model_resource_scheduler.status()
