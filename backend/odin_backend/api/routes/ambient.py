"""Milestone 5 ambient layer APIs."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["ambient"])


class CollaborationRequest(BaseModel):
    template: str = "research_report"
    objective: str


class OverlayContextRequest(BaseModel):
    application: str | None = None
    window: str | None = None


@router.get("/desktop-semantics/summary")
async def desktop_summary(request: Request) -> dict:
    app = request.app.state.odin
    session = app.context_engine.get_session()
    return app.desktop_semantics.summarize_current_workspace(session)


@router.get("/execution-intelligence/reliability")
async def reliability_scores(request: Request) -> list[dict]:
    app = request.app.state.odin
    return app.execution_intelligence.get_reliability_scores()


@router.get("/execution-intelligence/recommend/{tool_name}")
async def tool_recommendation(tool_name: str, request: Request) -> dict:
    app = request.app.state.odin
    return app.execution_intelligence.recommend_for_tool(tool_name)


@router.get("/cognitive-stream/timeline")
async def cognitive_timeline(request: Request, limit: int = 50, source: str | None = None) -> dict:
    app = request.app.state.odin
    return {
        "timeline": app.unified_cognition.timeline(limit, source),
        "active_paths": app.unified_cognition.active_reasoning_paths(),
    }


@router.post("/collaboration/chains")
async def create_collaboration(body: CollaborationRequest, request: Request) -> dict:
    app = request.app.state.odin
    chain = app.collaboration.create_chain(body.template, body.objective)
    if not chain:
        raise HTTPException(status_code=400, detail="Unknown template")
    return chain.model_dump(mode="json")


@router.get("/collaboration/chains")
async def list_collaboration(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [c.model_dump(mode="json") for c in app.collaboration.list_chains()]


@router.post("/memory/consolidate")
async def consolidate_memory(request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_consolidation.run_consolidation_pass()


@router.get("/proactive/recommendations")
async def list_recommendations(request: Request) -> list[dict]:
    app = request.app.state.odin
    recs = app.proactive.list_recommendations()
    if not recs and app.settings.proactive_recommendations_enabled:
        recs = await app.proactive.generate_recommendations()
    return [r.model_dump(mode="json") for r in recs]


@router.post("/proactive/recommendations/generate")
async def generate_recommendations(request: Request) -> list[dict]:
    app = request.app.state.odin
    recs = await app.proactive.generate_recommendations()
    return [r.model_dump(mode="json") for r in recs]


@router.post("/proactive/recommendations/{rec_id}/dismiss")
async def dismiss_recommendation(rec_id: str, request: Request) -> dict:
    app = request.app.state.odin
    ok = app.proactive.dismiss(rec_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return {"dismissed": True}


@router.get("/proactive/recommendations/{rec_id}/explain")
async def explain_recommendation(rec_id: str, request: Request) -> dict:
    app = request.app.state.odin
    expl = app.proactive.explain(rec_id)
    if not expl:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return expl


@router.get("/local-models/status")
async def local_model_status(request: Request) -> dict:
    app = request.app.state.odin
    return app.local_models.runtime_status()


@router.post("/local-models/warm")
async def warm_local_model(request: Request, model: str | None = None) -> dict:
    app = request.app.state.odin
    return await app.local_models.warm_model(model)


@router.get("/policies")
async def list_policies(request: Request) -> list[dict]:
    app = request.app.state.odin
    return [p.model_dump() for p in app.policy_engine.list_policies()]


@router.get("/overlay/actions")
async def overlay_contextual_actions(request: Request) -> dict:
    """Contextual productivity actions for command overlay."""
    app = request.app.state.odin
    session = app.context_engine.get_session()
    ws = app.workspace_intelligence.summarize_workspace(session)
    generated = app.workspace_automation.generate_actions(session, ws)
    app_name = ""
    if session and session.active_applications:
        app_name = session.active_applications[0].name.lower()
    return {
        "application": app_name,
        "context_enabled": app.context_engine.enabled,
        "collector_enabled": app.desktop_runtime.enabled,
        "insight": session.insight if session else None,
        "actions": generated["actions"],
        "workflow_suggestions": generated.get("workflow_suggestions", []),
        "explainable": generated.get("explainable", {}),
    }
