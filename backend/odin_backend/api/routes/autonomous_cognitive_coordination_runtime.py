"""Autonomous cognitive coordination APIs (Prompt 55)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["autonomous-cognitive-coordination-runtime"])


class ObjectiveCreateRequest(BaseModel):
    root: str
    children: list[str] = Field(default_factory=list)


class ObjectiveProgressRequest(BaseModel):
    objective_id: str
    progress: float = 0.0


class TaskHorizonRequest(BaseModel):
    task: str = "engineering"


@router.get("/autonomous-coordination")
async def autonomous_coordination_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"autonomous_coordination": app.autonomous_coordination.snapshot()}


@router.post("/autonomous-coordination/coordinate")
async def autonomous_coordination_coordinate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_coordination.coordinate_runtime_objectives()


@router.get("/autonomous-coordination/snapshot")
async def autonomous_coordination_snapshot(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_coordination.build_coordination_snapshot()


@router.post("/autonomous-coordination/recover")
async def autonomous_coordination_recover(request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_coordination.recover_interrupted_coordination()


@router.get("/objectives/active")
async def objectives_active(request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_management.summarize_active_objectives()


@router.post("/objectives/create")
async def objectives_create(body: ObjectiveCreateRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_management.create_objective_tree(root=body.root, children=body.children)


@router.post("/objectives/progress")
async def objectives_progress(body: ObjectiveProgressRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_management.update_objective_progress(
        objective_id=body.objective_id, progress=body.progress
    )


@router.get("/objectives/stalled")
async def objectives_stalled(request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_management.detect_stalled_objectives()


@router.get("/objective-graph")
async def objective_graph(request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_management.restore_objective_chain()


@router.get("/context-sync/state")
async def context_sync_state(request: Request) -> dict:
    app = request.app.state.odin
    return {"context_synchronization": app.context_synchronization.snapshot()}


@router.post("/context-sync/synchronize")
async def context_sync_synchronize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.context_synchronization.synchronize_context_surfaces()


@router.post("/context-sync/merge")
async def context_sync_merge(request: Request) -> dict:
    app = request.app.state.odin
    return await app.context_synchronization.merge_runtime_context()


@router.get("/context-sync/divergence")
async def context_sync_divergence(request: Request) -> dict:
    app = request.app.state.odin
    return await app.context_synchronization.detect_context_divergence()


@router.get("/mission-continuity/health")
async def mission_continuity_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_continuity.estimate_continuity_health()


@router.post("/mission-continuity/restore")
async def mission_continuity_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_continuity.restore_mission_context()


@router.get("/mission-continuity/resume-chain")
async def mission_continuity_resume_chain(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_continuity.build_mission_resume_chain()


@router.get("/continuity-health")
async def continuity_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_continuity.estimate_continuity_health()


@router.post("/cognitive-planning/generate")
async def cognitive_planning_generate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_planning.generate_cognitive_plan()


@router.get("/cognitive-planning/budget")
async def cognitive_planning_budget(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_planning.allocate_reasoning_budget()


@router.post("/cognitive-planning/horizon")
async def cognitive_planning_horizon(body: TaskHorizonRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_planning.estimate_task_horizon(task=body.task)


@router.get("/reasoning-budget")
async def reasoning_budget(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_planning": app.cognitive_planning.snapshot()}


@router.get("/operator-alignment")
async def operator_alignment(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_alignment.estimate_operator_alignment()


@router.post("/operator-alignment/adapt")
async def operator_alignment_adapt(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_alignment.adapt_assistance_strategy()


@router.get("/supervision-confidence")
async def supervision_confidence(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_alignment.compute_supervision_confidence()


@router.get("/operator-alignment/drift")
async def operator_alignment_drift(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_alignment.detect_alignment_drift()
