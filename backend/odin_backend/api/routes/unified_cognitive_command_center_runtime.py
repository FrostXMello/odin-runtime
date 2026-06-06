"""Unified cognitive command center APIs (Prompt 60)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["unified-cognitive-command-center-runtime"])


class PhaseRequest(BaseModel):
    phase: str = "execution"


class TimelineEventRequest(BaseModel):
    kind: str
    payload: dict | None = None


@router.get("/unified-command/status")
async def unified_command_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"unified_command_center": app.unified_command_center.snapshot()}


@router.post("/unified-command/synchronize")
async def unified_command_sync(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_command_center.synchronize_runtime_layers()


@router.post("/unified-command/initialize")
async def unified_command_init(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_command_center.initialize_command_center()


@router.get("/operational-health")
async def operational_health(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_command_center.compute_global_operational_health()


@router.get("/global-pressure")
async def global_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.unified_command_center.rebalance_command_pressure()


@router.get("/mission-command")
async def mission_command_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"mission_command": app.mission_command.snapshot()}


@router.post("/mission-command/phase")
async def mission_command_phase(body: PhaseRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_command.transition_operational_phase(phase=body.phase)


@router.get("/mission-command/pressure")
async def mission_command_pressure(request: Request) -> dict:
    app = request.app.state.odin
    return await app.mission_command.compute_mission_pressure()


@router.get("/mission-phases")
async def mission_phases(request: Request) -> dict:
    app = request.app.state.odin
    return {"mission_command": app.mission_command.snapshot()}


@router.post("/cognitive-multiplexing/multiplex")
async def cognitive_multiplexing_multiplex(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_multiplexing.multiplex_cognition_streams()


@router.post("/cognitive-multiplexing/compress")
async def cognitive_multiplexing_compress(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_multiplexing.compress_runtime_streams()


@router.get("/cognitive-multiplexing")
async def cognitive_multiplexing_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_multiplexing": app.cognitive_multiplexing.snapshot()}


@router.post("/runtime-fusion/fuse")
async def runtime_fusion_fuse(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_fusion.fuse_runtime_contexts()


@router.post("/runtime-fusion/restore")
async def runtime_fusion_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_fusion.restore_fused_operational_state()


@router.get("/runtime-fusion")
async def runtime_fusion_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"runtime_fusion": app.runtime_fusion.snapshot()}


@router.post("/operator-command-surfaces/render")
async def command_surfaces_render(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_command_surfaces.render_command_surface()


@router.get("/operator-command-surfaces/layout")
async def command_surfaces_layout(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_command_surfaces": app.operator_command_surfaces.snapshot()}


@router.get("/command-surfaces")
async def command_surfaces(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_command_surfaces.render_operational_overlay()


@router.get("/live-cognition-timeline")
async def live_cognition_timeline(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_cognition_timeline.build_operational_timeline()


@router.post("/live-cognition-timeline/replay")
async def live_cognition_timeline_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_cognition_timeline.replay_cognition_window()


@router.post("/live-cognition-timeline/append")
async def live_cognition_timeline_append(body: TimelineEventRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_cognition_timeline.append_cognition_event(kind=body.kind, payload=body.payload)


@router.get("/cognition-replay")
async def cognition_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_cognition_timeline.replay_cognition_window()
