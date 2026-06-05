"""Adaptive infrastructure APIs (Prompt 33)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["infrastructure-runtime"])


class OptimizeEvolutionRequest(BaseModel):
    pass


class ProjectOperationsRequest(BaseModel):
    goal: str
    horizon_weeks: int = 4


@router.get("/continuity")
async def runtime_continuity(request: Request) -> dict:
    app = request.app.state.odin
    return {"continuity": await app.continuity_runtime.snapshot()}


@router.get("/background-cognition")
async def runtime_background_cognition(request: Request) -> dict:
    app = request.app.state.odin
    return {"background": app.background_cognition.snapshot()}


@router.post("/background-cognition/run")
async def runtime_background_run(request: Request) -> dict:
    app = request.app.state.odin
    return await app.background_cognition.run_cycle()


@router.get("/evolution")
async def runtime_evolution(request: Request) -> dict:
    app = request.app.state.odin
    return {"evolution": app.evolution_runtime.snapshot()}


@router.post("/evolution/optimize")
async def runtime_evolution_optimize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_runtime.optimize()


@router.get("/economy")
async def runtime_economy(request: Request) -> dict:
    app = request.app.state.odin
    return {"economy": app.cognitive_economy.snapshot()}


@router.get("/meta-reasoning")
async def runtime_meta_reasoning(request: Request) -> dict:
    app = request.app.state.odin
    return {"meta": app.meta_reasoning.snapshot()}


@router.get("/operations")
async def runtime_operations(request: Request) -> dict:
    app = request.app.state.odin
    return {"operations": app.operational_planning.snapshot()}


@router.post("/operations/project")
async def runtime_operations_project(body: ProjectOperationsRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operational_planning.project(goal=body.goal, horizon_weeks=body.horizon_weeks)


@router.get("/operator-profile")
async def runtime_operator_profile(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator": await app.operator_relationship.snapshot()}


@router.get("/distributed-optimization")
async def runtime_distributed_optimization(request: Request) -> dict:
    app = request.app.state.odin
    return {"optimization": app.distributed_optimization.snapshot()}


@router.post("/distributed-optimization/optimize")
async def runtime_distributed_optimize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.distributed_optimization.optimize()
