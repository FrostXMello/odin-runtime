"""Planner and tool intelligence runtime APIs."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/runtime", tags=["planner-runtime"])


@router.get("/planner")
async def runtime_planner(request: Request) -> dict:
    app = request.app.state.odin
    planner = app.mission_planner.semantic
    missions = {}
    for mid in list(app.mission_manager._active.keys())[:20]:  # noqa: SLF001
        plan = planner.get_plan(mid)
        if plan:
            missions[mid] = {
                "confidence": plan.confidence,
                "strategy": plan.strategy,
                "reasoning_nodes": plan.reasoning.get("node_count", 0),
            }
    worker = getattr(app, "mission_worker", None)
    planner_metrics = {}
    if hasattr(app, "mission_worker"):
        pw = getattr(app.mission_worker, "_planner_worker", None)
        if pw:
            planner_metrics = pw.metrics
    return {
        "active_plans": len(missions),
        "missions": missions,
        "planner_worker_metrics": planner_metrics,
        "adaptive": app.mission_execution_adaptive.snapshot(app),
    }


@router.get("/tools")
async def runtime_tools(request: Request) -> dict:
    app = request.app.state.odin
    reg = app.intelligent_tool_registry
    selector = app.tool_selector
    health = await reg.health()
    return {
        "health": health,
        "tools": [t.to_dict() for t in reg.list_all()],
        "capabilities": reg.advertise_capabilities(),
        "recent_selections": selector.recent_decisions,
    }


@router.get("/strategies")
async def runtime_strategies(request: Request) -> dict:
    app = request.app.state.odin
    strategies: list[dict] = []
    for mid, mission in list(app.mission_manager._active.items())[:30]:  # noqa: SLF001
        sp = mission.metadata.get("semantic_plan") or {}
        strategies.append(
            {
                "mission_id": mid,
                "strategy": sp.get("strategy") or {"kind": mission.execution_strategy},
                "confidence": mission.confidence,
                "confidence_actions": sp.get("confidence_actions"),
            }
        )
    return {"count": len(strategies), "strategies": strategies}


@router.get("/planner/missions/{mission_id}/reasoning-graph")
async def mission_reasoning_graph(mission_id: str, request: Request) -> dict:
    app = request.app.state.odin
    plan = app.mission_planner.get_semantic_plan(mission_id)
    if not plan:
        mission = await app.mission_manager.get(mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="mission not found")
        return {
            "mission_id": mission_id,
            "reasoning": mission.metadata.get("semantic_plan", {}).get("reasoning", {}),
            "reasoning_log": mission.reasoning_log,
        }
    return {
        "mission_id": mission_id,
        "reasoning": plan.reasoning,
        "confidence": plan.confidence,
        "contracts": plan.contracts,
        "capability_requirements": plan.capability_requirements,
    }
