"""Live cognitive orchestration APIs (Prompt 56)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["live-cognitive-orchestration-runtime"])


class LinkRequest(BaseModel):
    src: str
    dst: str


@router.get("/live-orchestration")
async def live_orchestration_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_orchestration": app.live_orchestration.snapshot()}


@router.post("/live-orchestration/stream")
async def live_orchestration_stream(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_orchestration.stream_orchestration_state()


@router.get("/live-orchestration/health")
async def live_orchestration_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_orchestration.compute_orchestration_health()


@router.post("/live-orchestration/pulse")
async def live_orchestration_pulse(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_orchestration.render_cognition_pulse()


@router.get("/live-orchestration/instability")
async def live_orchestration_instability(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_orchestration.detect_runtime_instability()


@router.get("/objective-streams")
async def objective_streams_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"objective_streams": app.objective_streams.snapshot()}


@router.post("/objective-streams/stream")
async def objective_streams_stream(request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_streams.stream_objective_updates()


@router.post("/objective-streams/reprioritize")
async def objective_streams_reprioritize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_streams.reprioritize_active_objectives()


@router.get("/objective-streams/stagnation")
async def objective_streams_stagnation(request: Request) -> dict:
    app = request.app.state.odin
    return await app.objective_streams.detect_objective_stagnation()


@router.get("/mission-graph")
async def mission_graph_status(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_graph.build_mission_graph()


@router.post("/mission-graph/link")
async def mission_graph_link(body: LinkRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_graph.link_related_objectives(src=body.src, dst=body.dst)


@router.get("/mission-graph/pressure")
async def mission_graph_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_graph.analyze_dependency_pressure()


@router.get("/mission-graph/continuity")
async def mission_graph_continuity(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_graph.compute_mission_continuity_score()


@router.get("/realtime-coordination")
async def realtime_coordination_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"realtime_coordination": app.realtime_coordination.snapshot()}


@router.post("/realtime-coordination/multiplex")
async def realtime_coordination_multiplex(request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_coordination.multiplex_runtime_streams()


@router.post("/realtime-coordination/stabilize")
async def realtime_coordination_stabilize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_coordination.stabilize_coordination_loops()


@router.get("/realtime-coordination/pressure")
async def realtime_coordination_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.realtime_coordination.estimate_coordination_pressure()


@router.get("/operator-awareness")
async def operator_awareness(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_situational_awareness.generate_operator_brief()


@router.get("/operator-awareness/pressure")
async def operator_awareness_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_situational_awareness.estimate_operational_pressure()


@router.get("/operational-pressure")
async def operational_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_situational_awareness.estimate_operational_pressure()


@router.get("/operator-awareness/focus-risk")
async def operator_awareness_focus_risk(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_situational_awareness.forecast_focus_instability()


@router.get("/cognitive-visual-layers")
async def cognitive_visual_layers(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_visual_layers": app.cognitive_visual_layers.snapshot()}


@router.post("/cognitive-visual-layers/constellation")
async def visual_constellation(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_visual_layers.render_runtime_constellation()


@router.post("/cognitive-visual-layers/river")
async def visual_river(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_visual_layers.render_objective_river()


@router.get("/runtime-constellation")
async def runtime_constellation(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_visual_layers.render_runtime_constellation()


@router.get("/objective-river")
async def objective_river(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_visual_layers.render_objective_river()


@router.get("/cognition-pulse")
async def cognition_pulse(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_orchestration.render_cognition_pulse()


@router.get("/live-mission-timeline")
async def live_mission_timeline(request: Request) -> dict:
    app = request.app.state.odin
    graph = await app.mission_graph.build_mission_graph()
    continuity = await app.mission_graph.compute_mission_continuity_score()
    return {"graph": graph, "continuity": continuity}
