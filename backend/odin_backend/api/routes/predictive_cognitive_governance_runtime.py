"""Predictive cognitive governance APIs (Prompt 59)."""

from fastapi import APIRouter, Request

router = APIRouter(prefix="/runtime", tags=["predictive-cognitive-governance-runtime"])


@router.get("/predictive-governance/status")
async def predictive_governance_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"predictive_governance": app.predictive_governance.snapshot()}


@router.post("/predictive-governance/rebalance")
async def predictive_governance_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.predictive_governance.rebalance_governance_pressure()


@router.post("/predictive-governance/initialize")
async def predictive_governance_initialize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.predictive_governance.initialize_governance_cycle()


@router.get("/governance-health")
async def governance_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.predictive_governance.compute_governance_health()


@router.post("/runtime-stabilization/stabilize")
async def runtime_stabilization_stabilize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_stabilization.stabilize_runtime_pressure()


@router.get("/runtime-stabilization/health")
async def runtime_stabilization_health(request: Request) -> dict:
    app = request.app.state.odin
    inst = await app.runtime_stabilization.detect_runtime_instability()
    return {"runtime_stabilization": app.runtime_stabilization.snapshot(), "instability": inst}


@router.post("/runtime-stabilization/cooldown")
async def runtime_stabilization_cooldown(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_stabilization.trigger_governance_cooldown()


@router.post("/cognitive-risk/forecast")
async def cognitive_risk_forecast(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_risk.forecast_cognitive_risk()


@router.post("/cognitive-risk/simulate")
async def cognitive_risk_simulate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_risk.simulate_failure_chain()


@router.get("/cognitive-risk/surface")
async def cognitive_risk_surface(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_risk.compute_risk_surface()


@router.get("/failure-simulation")
async def failure_simulation(request: Request) -> dict:
    app = request.app.state.odin
    forecast = await app.cognitive_risk.forecast_cognitive_risk()
    simulate = await app.cognitive_risk.simulate_failure_chain()
    return {"forecast": forecast, "simulation": simulate}


@router.get("/trust-surfaces")
async def trust_surfaces(request: Request) -> dict:
    app = request.app.state.odin
    return await app.trust_surfaces.compute_operator_trust()


@router.get("/trust-surfaces/confidence")
async def trust_surfaces_confidence(request: Request) -> dict:
    app = request.app.state.odin
    return await app.trust_surfaces.surface_governance_confidence()


@router.get("/supervision-integrity")
async def supervision_integrity(request: Request) -> dict:
    app = request.app.state.odin
    return await app.trust_surfaces.estimate_supervision_integrity()


@router.get("/execution-confidence")
async def execution_confidence(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_confidence.estimate_execution_confidence()


@router.post("/execution-confidence/forecast")
async def execution_confidence_forecast(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_confidence.forecast_workflow_completion()


@router.get("/workflow-forecast")
async def workflow_forecast(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_confidence.forecast_workflow_completion()


@router.post("/governance-visualization/render")
async def governance_visualization_render(request: Request) -> dict:
    app = request.app.state.odin
    return await app.governance_visualization.render_governance_surface()


@router.get("/governance-visualization")
async def governance_visualization_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"governance_visualization": app.governance_visualization.snapshot()}
