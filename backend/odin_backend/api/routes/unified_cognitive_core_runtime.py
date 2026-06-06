"""Unified cognitive core APIs (Prompt 52)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["unified-cognitive-core-runtime"])


class FocusRequest(BaseModel):
    focus: str = "workspace"


class ProfileRequest(BaseModel):
    profile: str = "balanced"


class TaskRequest(BaseModel):
    task: str
    queue: str = "active"


class DeferRequest(BaseModel):
    task: str


class AssignRequest(BaseModel):
    agent_id: str
    objective: str


class WorkloadRequest(BaseModel):
    agent_id: str
    workload: float = 0.5


class AgentIdRequest(BaseModel):
    agent_id: str


@router.get("/unified-core/status")
async def unified_core_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"unified_cognitive_core": app.unified_cognitive_core.snapshot()}


@router.post("/unified-core/tick")
async def unified_core_tick(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_cognitive_core.cognition_tick()


@router.post("/unified-core/synchronize")
async def unified_core_synchronize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_cognitive_core.synchronize_runtimes()


@router.post("/unified-core/rebuild-context")
async def unified_core_rebuild_context(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_cognitive_core.rebuild_context()


@router.post("/unified-core/checkpoint")
async def unified_core_checkpoint(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_cognitive_core.checkpoint_global_state()


@router.get("/cognition-heartbeat")
async def cognition_heartbeat(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_cognitive_core.cognition_tick()


@router.get("/global-context")
async def global_context(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_cognitive_core.rebuild_context()


@router.get("/active-objectives")
async def active_objectives(request: Request) -> dict:
    app = request.app.state.odin
    snap = app.unified_cognitive_core.snapshot()
    return {"accepted": True, "objectives": snap.get("objectives", 0)}


@router.get("/attention")
async def attention_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"attention_engine": app.attention_engine.snapshot()}


@router.post("/attention/shift")
async def attention_shift(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.attention_engine.shift_attention(focus=body.focus)


@router.get("/attention/heatmap")
async def attention_heatmap(request: Request) -> dict:
    app = request.app.state.odin
    return await app.attention_engine.compute_focus_heatmap()


@router.post("/attention/profile")
async def attention_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.attention_engine.set_profile(body.profile)


@router.get("/cognitive-scheduler")
async def cognitive_scheduler_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_scheduler": app.cognitive_scheduler.snapshot()}


@router.post("/cognitive-scheduler/schedule")
async def cognitive_scheduler_schedule(body: TaskRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_scheduler.schedule_cognition(task=body.task, queue=body.queue)


@router.post("/cognitive-scheduler/defer")
async def cognitive_scheduler_defer(body: DeferRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_scheduler.defer_task(task=body.task)


@router.post("/cognitive-scheduler/restore")
async def cognitive_scheduler_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_scheduler.restore_deferred_tasks()


@router.post("/cognitive-scheduler/rebalance")
async def cognitive_scheduler_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_scheduler.rebalance_runtime_load()


@router.get("/persistent-agents")
async def persistent_agents_list(request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_agents.restore_agents()


@router.post("/persistent-agents/assign")
async def persistent_agents_assign(body: AssignRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_agents.assign_objective(agent_id=body.agent_id, objective=body.objective)


@router.post("/persistent-agents/workload")
async def persistent_agents_workload(body: WorkloadRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_agents.update_agent_state(agent_id=body.agent_id, workload=body.workload)


@router.get("/persistent-agents/load")
async def persistent_agents_load(request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_agents.compute_agent_load()


@router.post("/persistent-agents/summarize")
async def persistent_agents_summarize(body: AgentIdRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.persistent_agents.summarize_agent_memory(agent_id=body.agent_id)


@router.get("/runtime-coordination")
async def runtime_coordination_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"runtime_coordination": app.runtime_coordination.snapshot()}


@router.get("/runtime-coordination/conflicts")
async def runtime_coordination_conflicts(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_coordination.detect_runtime_overlap()


@router.post("/runtime-coordination/merge")
async def runtime_coordination_merge(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_coordination.merge_contexts()


@router.post("/runtime-coordination/resolve")
async def runtime_coordination_resolve(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_coordination.resolve_priority_conflicts()


@router.get("/cognitive-state")
async def cognitive_state_get(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_state.compute_cognitive_state()


@router.get("/cognitive-state/snapshot")
async def cognitive_state_snapshot(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_state.export_state_snapshot()


@router.get("/focus-heatmap")
async def focus_heatmap(request: Request) -> dict:
    app = request.app.state.odin
    return await app.attention_engine.compute_focus_heatmap()
