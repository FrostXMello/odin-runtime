"""Milestone 6 environment APIs."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["environment"])


class TrustAssessRequest(BaseModel):
    tool_name: str
    params: dict | None = None
    workflow_id: str | None = None


@router.get("/workspace-intelligence/summary")
async def workspace_summary(request: Request) -> dict:
    app = request.app.state.odin
    ctx = app.context_engine.get_session()
    summary = app.workspace_intelligence.summarize_workspace(ctx)
    return summary


@router.get("/live-cognition/state")
async def live_cognition_state(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "attention": app.live_cognition.get_current_attention(),
        "operational": app.live_cognition.summarize_operational_state(),
        "focus_graph": app.live_cognition.get_active_focus_graph(),
    }


@router.get("/resilience/status")
async def resilience_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"circuit_breakers": app.resilience.breaker_status()}


@router.get("/agent-society")
async def agent_society(request: Request) -> dict:
    app = request.app.state.odin
    return {"agents": app.agent_society.list_profiles()}


@router.get("/agent-society/{agent_id}/reputation")
async def agent_reputation(agent_id: str, request: Request) -> dict:
    app = request.app.state.odin
    rep = app.agent_society.get_reputation(agent_id)
    if not rep:
        raise HTTPException(status_code=404, detail="Agent not found")
    return rep


@router.post("/agent-society/route")
async def route_task(domain: str, request: Request, context: str = "") -> dict:
    app = request.app.state.odin
    agent = app.agent_society.route_task(domain, context=context)
    return {"domain": domain, "routed_agent": str(agent), "explainable": "ODIN supreme orchestrator delegates"}

@router.get("/compute/dashboard")
async def compute_dashboard(request: Request) -> dict:
    app = request.app.state.odin
    return app.compute.runtime_dashboard()


@router.get("/memory-evolution/timeline")
async def memory_timeline(request: Request, limit: int = 50) -> list[dict]:
    app = request.app.state.odin
    return app.memory_evolution.get_behavioral_timeline(limit)


@router.post("/memory-evolution/consolidate")
async def memory_evolution_report(request: Request) -> dict:
    app = request.app.state.odin
    patterns = await app.memory_evolution.extract_long_term_patterns()
    weekly = await app.memory_evolution.generate_weekly_summary()
    return {"patterns": patterns, "weekly_summary": weekly}


@router.get("/personalization/evolution")
async def personalization_evolution(request: Request) -> dict:
    app = request.app.state.odin
    return app.preference_evolution.adapt_response_style()


@router.post("/trust/assess")
async def trust_assess(body: TrustAssessRequest, request: Request) -> dict:
    app = request.app.state.odin
    assessment = await app.trust_system.assess_execution(
        body.tool_name,
        params=body.params,
        workflow_id=body.workflow_id,
    )
    return assessment.model_dump()


@router.get("/trust/dashboard")
async def trust_dashboard(request: Request) -> dict:
    app = request.app.state.odin
    return app.trust_system.dashboard()


@router.get("/workspace-automation/actions")
async def workspace_actions(request: Request) -> dict:
    app = request.app.state.odin
    ctx = app.context_engine.get_session()
    ws = app.workspace_intelligence.summarize_workspace(ctx)
    return app.workspace_automation.generate_actions(ctx, ws)
