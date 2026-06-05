"""Persistent mission API."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from odin_backend.core.missions.manager import MissionDuplicateError

router = APIRouter(prefix="/missions", tags=["missions"])


class MissionCreateRequest(BaseModel):
    objective: str
    priority: int = Field(default=50, ge=0, le=100)
    autonomy_level: int = Field(default=1, ge=0, le=5)
    created_by: str = "user"
    human_approved: bool = False
    start_worker: bool = True
    mission_type: str = "standard"
    originating_signal: str = "api"
    planning_context: str = ""


class MissionResponse(BaseModel):
    mission_id: str
    objective: str
    current_state: str
    priority: int
    active_tasks: list[dict]
    completed_tasks: list[dict]


def _to_response(mission) -> MissionResponse:
    return MissionResponse(
        mission_id=mission.mission_id,
        objective=mission.objective,
        current_state=mission.current_state.value,
        priority=mission.priority,
        active_tasks=[t.model_dump(mode="json") for t in mission.active_tasks],
        completed_tasks=[t.model_dump(mode="json") for t in mission.completed_tasks],
    )


def _enqueue(app, mission_id: str) -> None:
    app.mission_worker.enqueue_mission(mission_id)


@router.post("/create", response_model=MissionResponse)
async def create_mission(body: MissionCreateRequest, request: Request) -> MissionResponse:
    app = request.app.state.odin
    try:
        result = await app.mission_manager.create_checked(
            body.objective,
            priority=body.priority,
            autonomy_level=body.autonomy_level,
            created_by=body.created_by,
            human_approved=body.human_approved,
            mission_type=body.mission_type,
            originating_signal=body.originating_signal,
            planning_context=body.planning_context,
        )
    except MissionDuplicateError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "error": str(exc),
                "duplicate_mission_id": exc.duplicate_mission_id,
                "action": exc.action,
            },
        ) from exc

    if result.suppressed:
        raise HTTPException(
            status_code=409,
            detail={
                "error": "duplicate mission suppressed",
                "duplicate_mission_id": result.duplicate_of,
                "action": "duplicate_active",
            },
        )

    if body.start_worker:
        _enqueue(app, result.mission.mission_id)
    return _to_response(result.mission)


@router.get("", response_model=list[MissionResponse])
async def list_missions(request: Request, limit: int = 50) -> list[MissionResponse]:
    app = request.app.state.odin
    missions = await app.mission_manager.list_missions(limit=limit)
    return [_to_response(m) for m in missions]


@router.get("/{mission_id}", response_model=dict)
async def get_mission(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission.model_dump(mode="json")


@router.post("/{mission_id}/pause")
async def pause_mission(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.pause(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {"mission_id": mission_id, "state": mission.current_state.value}


@router.post("/{mission_id}/resume")
async def resume_mission(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.resume(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    _enqueue(app, mission_id)
    return {"mission_id": mission_id, "state": mission.current_state.value}


@router.post("/{mission_id}/cancel")
async def cancel_mission(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    cancelled_execs = await app.mission_execution_bridge.cancel_mission_executions(mission_id)
    mission = await app.mission_manager.cancel(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return {
        "mission_id": mission_id,
        "state": mission.current_state.value,
        "executions_cancelled": cancelled_execs,
    }


@router.post("/{mission_id}/approve")
async def approve_mission(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.approve(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    _enqueue(app, mission_id)
    return {"mission_id": mission_id, "state": mission.current_state.value, "approved": True}


@router.get("/{mission_id}/executions")
async def mission_executions(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    executions = await app.mission_execution_bridge.list_mission_executions(mission_id)
    deps = app.mission_execution_bridge.planner.dependency_snapshot(mission)
    return {"mission_id": mission_id, "count": len(executions), "executions": executions, "dependencies": deps}


@router.get("/{mission_id}/timeline")
async def mission_timeline(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    from odin_backend.core.observability.timeline import build_mission_timeline

    events = app.observability.tracer.store.get_mission_events(mission_id)
    timeline = build_mission_timeline(mission, events)
    checkpoints = await app.mission_store.list_checkpoints(mission_id, limit=30)
    memory_audit = [
        m.model_dump(mode="json")
        for m in app.observability.memory_audit.for_mission(mission_id, limit=50)
    ]
    timeline["checkpoints"] = checkpoints
    timeline["memory_mutations"] = memory_audit
    return timeline


@router.get("/{mission_id}/tasks/{task_id}/timeline")
async def mission_task_timeline(mission_id: str, task_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission or not mission.task_graph.get(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    from odin_backend.core.observability.timeline import build_task_timeline

    events = app.observability.tracer.store.get_task_events(task_id)
    return build_task_timeline(mission, task_id, events)


@router.get("/{mission_id}/adaptation-log")
async def mission_adaptation_log(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    strategies = app.perception_memory.strategies_for(mission_id)
    return {
        "mission_id": mission_id,
        "execution_strategy": mission.execution_strategy,
        "confidence": mission.confidence,
        "adaptation_log": mission.adaptation_log,
        "strategy_records": strategies,
    }


@router.get("/{mission_id}/reasoning")
async def mission_reasoning(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    replay = await app.mission_memory.replay(mission_id)
    semantic = app.mission_planner.get_semantic_plan(mission_id)
    ctx = await app.mission_context.build_context(mission) if hasattr(app, "mission_context") else {}
    return {
        "mission_id": mission_id,
        "reasoning_log": mission.reasoning_log,
        "memory_refs": mission.memory_refs,
        "memory_replay": replay,
        "semantic_plan": semantic.model_dump(mode="json") if semantic else mission.metadata.get("semantic_plan"),
        "reasoning_graph": semantic.reasoning if semantic else {},
        "planner_context": ctx,
        "confidence": mission.confidence,
    }


@router.get("/{mission_id}/retrospective")
async def mission_retrospective(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    retro = mission.metadata.get("retrospective")
    if not retro and mission.is_terminal():
        retro = await app.experience_engine.on_mission_completed(mission)
        await app.mission_manager.persist(mission)
    return {"mission_id": mission_id, "retrospective": retro or {}}


@router.get("/{mission_id}/memory-context")
async def mission_memory_context(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    ctx = await app.mission_context.build_context(mission)
    similar = await app.memory_retrieval.similar_executions(mission.objective, limit=5)
    return {"mission_id": mission_id, "context": ctx, "similar_executions": similar}


@router.get("/{mission_id}/reasoning-chain")
async def mission_reasoning_chain(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    chain = app.cognitive_agents.get_chain(mission_id)
    if not chain:
        pipeline = await app.cognitive_agents.run_pipeline(
            objective=mission.objective,
            mission_id=mission_id,
        )
        chain = pipeline.get("steps", [])
    return {"mission_id": mission_id, "reasoning_chain": chain}


@router.get("/{mission_id}/reflection")
async def mission_reflection(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    reflections = app.cognitive_reflection.get_reflections(mission_id)
    plan = mission.metadata.get("semantic_plan", {}).get("summary", mission.objective)
    if not reflections:
        reflections = [
            await app.cognitive_reflection.reflect(
                plan=str(plan),
                objective=mission.objective,
                mission_id=mission_id,
            )
        ]
    return {"mission_id": mission_id, "reflections": reflections}


@router.get("/{mission_id}/memory-grounding")
async def mission_memory_grounding(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    mission = await app.mission_manager.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    grounding = await app.reasoning_pipeline.build(
        objective=mission.objective,
        mission_id=mission_id,
    )
    return {"mission_id": mission_id, "grounding": grounding}


@router.get("/{mission_id}/knowledge")
async def mission_knowledge(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    nodes = await app.knowledge_runtime.list_knowledge(limit=100)
    filtered = [n for n in nodes if n.get("mission_origin") == mission_id]
    return {"mission_id": mission_id, "knowledge": filtered}


@router.get("/{mission_id}/research")
async def mission_research(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    sessions = app.research_fabric.snapshot().get("sessions", [])
    filtered = [s for s in sessions if s.get("mission_id") == mission_id]
    return {"mission_id": mission_id, "research_sessions": filtered}


@router.get("/{mission_id}/beliefs")
async def mission_beliefs(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    beliefs = app.knowledge_runtime.snapshot().get("beliefs", [])
    nodes = await app.knowledge_runtime.list_knowledge(limit=100)
    mission_beliefs = [n for n in nodes if n.get("mission_origin") == mission_id]
    return {"mission_id": mission_id, "beliefs": beliefs, "mission_facts": mission_beliefs}


@router.get("/{mission_id}/collaboration")
async def mission_collaboration(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    delegations = [d for d in app.agent_society._delegations.list_all() if d.get("mission_id") == mission_id]
    return {"mission_id": mission_id, "delegations": delegations, "graph": app.agent_society._graph.snapshot()}


@router.get("/{mission_id}/dialogues")
async def mission_dialogues(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    return {"mission_id": mission_id, "messages": app.agent_messages.dialogues()[-20:]}


@router.get("/{mission_id}/delegation")
async def mission_delegation(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    delegations = [d for d in app.agent_society._delegations.list_all() if d.get("mission_id") == mission_id]
    return {"mission_id": mission_id, "delegations": delegations}


@router.get("/{mission_id}/simulation")
async def mission_simulation(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    predictions = app.world_simulation.predictions_for_mission(mission_id)
    return {"mission_id": mission_id, "predictions": predictions, "simulations": app.world_simulation.list_simulations()[-5:]}


@router.get("/{mission_id}/strategy")
async def mission_strategy(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    return {"mission_id": mission_id, "analyses": app.strategic_reasoning.analysis_for_mission(mission_id)}


@router.get("/{mission_id}/federation")
async def mission_federation(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    delegations = app.society_federation._delegations.list_for_mission(mission_id)
    reasoning = app.society_federation._reasoning.list_for_mission(mission_id)
    return {"mission_id": mission_id, "delegations": delegations, "remote_reasoning": reasoning}
