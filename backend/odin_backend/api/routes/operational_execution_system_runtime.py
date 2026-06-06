"""Operational execution system APIs (Prompt 57)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["operational-execution-system-runtime"])


class PipelineRequest(BaseModel):
    stages: list[str] = Field(default_factory=lambda: ["plan", "review", "execute"])


class CollaborationRequest(BaseModel):
    task: str
    agents: list[str] = Field(default_factory=lambda: ["Planner", "Reviewer"])


class AgentRouteRequest(BaseModel):
    agent: str = "Planner"


class ChainRequest(BaseModel):
    chain_id: str
    stages: list[str] = Field(default_factory=list)
    success: bool = False


@router.get("/execution-system")
async def execution_system_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"execution_system": app.execution_system.snapshot()}


@router.post("/execution-system/start")
async def execution_system_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_system.initialize_execution_pipeline()


@router.post("/execution-system/checkpoint")
async def execution_system_checkpoint(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_system.checkpoint_execution_state()


@router.post("/execution-system/rollback")
async def execution_system_rollback(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_system.rollback_execution_stage()


@router.get("/execution-system/health")
async def execution_system_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_system.compute_execution_health()


@router.get("/task-orchestration/queue")
async def task_orchestration_queue(request: Request) -> dict:
    app = request.app.state.odin
    return {"task_orchestration": app.task_orchestration.snapshot()}


@router.post("/task-orchestration/pipeline")
async def task_orchestration_pipeline(body: PipelineRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.task_orchestration.build_execution_pipeline(stages=body.stages)


@router.post("/task-orchestration/rebalance")
async def task_orchestration_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.task_orchestration.reprioritize_execution_queue()


@router.get("/task-orchestration/blockers")
async def task_orchestration_blockers(request: Request) -> dict:
    app = request.app.state.odin
    return await app.task_orchestration.detect_execution_blockers()


@router.get("/execution-pipeline")
async def execution_pipeline(request: Request) -> dict:
    app = request.app.state.odin
    return await app.task_orchestration.build_execution_pipeline()


@router.post("/agent-collaboration/initiate")
async def agent_collaboration_initiate(body: CollaborationRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_collaboration.initiate_agent_collaboration(task=body.task, agents=body.agents)


@router.get("/agent-collaboration/consensus")
async def agent_collaboration_consensus(request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_collaboration.compute_consensus_score()


@router.get("/consensus-center")
async def consensus_center(request: Request) -> dict:
    app = request.app.state.odin
    consensus = await app.agent_collaboration.compute_consensus_score()
    summary = await app.agent_collaboration.summarize_agent_reasoning()
    return {"consensus": consensus, "reasoning": summary}


@router.post("/agent-collaboration/route")
async def agent_collaboration_route(body: AgentRouteRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.agent_collaboration.route_specialized_execution(agent=body.agent)


@router.get("/workspace-operations/state")
async def workspace_operations_state(request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_operations.build_workspace_operation_snapshot()


@router.post("/workspace-operations/recover")
async def workspace_operations_recover(request: Request) -> dict:
    app = request.app.state.odin
    return await app.workspace_operations.recover_workspace_operation()


@router.get("/execution-memory/history")
async def execution_memory_history(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_memory.resurface_successful_execution_patterns()


@router.post("/execution-memory/persist")
async def execution_memory_persist(body: ChainRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_memory.persist_execution_chain(
        chain_id=body.chain_id, stages=body.stages, success=body.success
    )


@router.post("/execution-memory/replay")
async def execution_memory_replay(body: ChainRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_memory.replay_execution_sequence(chain_id=body.chain_id)


@router.get("/execution-replay")
async def execution_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_memory.resurface_successful_execution_patterns()


@router.get("/execution-visibility/heatmap")
async def execution_visibility_heatmap(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_execution_visibility.render_execution_heatmap()


@router.get("/execution-visibility")
async def execution_visibility(request: Request) -> dict:
    app = request.app.state.odin
    return {"runtime_execution_visibility": app.runtime_execution_visibility.snapshot()}


@router.get("/execution-pressure")
async def execution_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_execution_visibility.compute_execution_pressure()
