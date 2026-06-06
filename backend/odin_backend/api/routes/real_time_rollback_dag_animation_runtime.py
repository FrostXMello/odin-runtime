"""Real-time rollback DAG animation engine APIs (Prompt 63)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/runtime", tags=["real-time-rollback-dag-animation-runtime"])


class FailureChainRequest(BaseModel):
    path: str = "default"


class ReplayWindowRequest(BaseModel):
    window_id: str = "replay-window"


class ReconstructRequest(BaseModel):
    execution_id: str = "exec-local"


@router.get("/rollback-animation")
async def rollback_animation_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"rollback_animation_engine": app.rollback_animation_engine.snapshot()}


@router.post("/rollback-animation/replay")
async def rollback_animation_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_animation_engine.replay_execution_chain()


@router.post("/rollback-animation/stabilize")
async def rollback_animation_stabilize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_animation_engine.stabilize_rollback_render()


@router.get("/rollback-animation/graph")
async def rollback_animation_graph(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_animation_engine.animate_rollback_graph()


@router.post("/rollback-animation/synchronize")
async def rollback_animation_synchronize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_animation_engine.synchronize_animation_frame()


@router.get("/rollback-dag-live")
async def rollback_dag_live(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_animation_engine.animate_rollback_graph()


@router.get("/execution-replay")
async def execution_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.rollback_animation_engine.replay_execution_chain()


@router.get("/causality-mapping/graph")
async def causality_mapping_graph(request: Request) -> dict:
    app = request.app.state.odin
    return await app.causality_mapping.build_causality_graph()


@router.post("/causality-mapping/failure-chain")
async def causality_mapping_failure_chain(body: FailureChainRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.causality_mapping.trace_failure_chain(path=body.path)


@router.get("/causality-mapping")
async def causality_mapping_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"causality_mapping": app.causality_mapping.snapshot()}


@router.get("/failure-lineage")
async def failure_lineage(request: Request) -> dict:
    app = request.app.state.odin
    return await app.causality_mapping.trace_failure_chain()


@router.get("/runtime-dependencies")
async def runtime_dependencies(request: Request) -> dict:
    app = request.app.state.odin
    return await app.causality_mapping.map_runtime_dependencies()


@router.post("/replay-orchestration/window")
async def replay_orchestration_window(body: ReplayWindowRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.replay_orchestration.initialize_replay_window(window_id=body.window_id)


@router.post("/replay-orchestration/throttle")
async def replay_orchestration_throttle(request: Request) -> dict:
    app = request.app.state.odin
    return await app.replay_orchestration.throttle_replay_density()


@router.get("/replay-orchestration")
async def replay_orchestration_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"replay_orchestration": app.replay_orchestration.snapshot()}


@router.post("/replay-orchestration/replay")
async def replay_orchestration_replay(request: Request) -> dict:
    app = request.app.state.odin
    return await app.replay_orchestration.replay_cognition_timeline()


@router.post("/replay-orchestration/checkpoint")
async def replay_orchestration_checkpoint(request: Request) -> dict:
    app = request.app.state.odin
    return await app.replay_orchestration.checkpoint_replay_state()


@router.get("/pressure-propagation/state")
async def pressure_propagation_state(request: Request) -> dict:
    app = request.app.state.odin
    return await app.pressure_propagation.propagate_runtime_pressure()


@router.post("/pressure-propagation/rebalance")
async def pressure_propagation_rebalance(request: Request) -> dict:
    app = request.app.state.odin
    return await app.pressure_propagation.rebalance_pressure_surfaces()


@router.get("/pressure-propagation")
async def pressure_propagation_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"pressure_propagation": app.pressure_propagation.snapshot()}


@router.get("/pressure-diffusion")
async def pressure_diffusion(request: Request) -> dict:
    app = request.app.state.odin
    return await app.pressure_propagation.simulate_pressure_diffusion()


@router.post("/pressure-propagation/congestion")
async def pressure_propagation_congestion(request: Request) -> dict:
    app = request.app.state.odin
    return await app.pressure_propagation.detect_congestion_chain()


@router.get("/timeline-visualization/render")
async def timeline_visualization_render(request: Request) -> dict:
    app = request.app.state.odin
    return await app.timeline_visualization.render_operational_timeline()


@router.post("/timeline-visualization/compress")
async def timeline_visualization_compress(request: Request) -> dict:
    app = request.app.state.odin
    return await app.timeline_visualization.compress_timeline_window()


@router.get("/timeline-visualization")
async def timeline_visualization_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"timeline_visualization": app.timeline_visualization.snapshot()}


@router.post("/timeline-visualization/synchronize")
async def timeline_visualization_synchronize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.timeline_visualization.synchronize_timeline_layers()


@router.get("/cognition-timeline")
async def cognition_timeline(request: Request) -> dict:
    app = request.app.state.odin
    return await app.timeline_visualization.render_operational_timeline()


@router.post("/execution-reconstruction/reconstruct")
async def execution_reconstruction_reconstruct(body: ReconstructRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_reconstruction.reconstruct_execution_state(execution_id=body.execution_id)


@router.post("/execution-reconstruction/restore")
async def execution_reconstruction_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_reconstruction.restore_cognition_window()


@router.get("/execution-reconstruction")
async def execution_reconstruction_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"execution_reconstruction": app.execution_reconstruction.snapshot()}


@router.post("/execution-reconstruction/simulate")
async def execution_reconstruction_simulate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_reconstruction.simulate_execution_restore()


@router.post("/execution-reconstruction/rebuild")
async def execution_reconstruction_rebuild(request: Request) -> dict:
    app = request.app.state.odin
    return await app.execution_reconstruction.rebuild_workspace_sequence()
