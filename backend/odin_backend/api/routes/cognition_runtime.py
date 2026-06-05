"""Cognitive learning and self-improvement runtime APIs."""

from fastapi import APIRouter, HTTPException, Request

router = APIRouter(prefix="/runtime", tags=["cognition-runtime"])


@router.get("/cognition")
async def runtime_cognition(request: Request) -> dict:
    app = request.app.state.odin
    graph = await app.cognitive_memory.export_snapshot(limit=80)
    return {
        "memory_graph": graph,
        "experience_metrics": app.experience_engine.metrics,
    }


@router.get("/learning")
async def runtime_learning(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "strategy_stats": app.experience_engine.strategy_stats(),
        "improvement_cycles": app.improvement_loop.cycle_count,
        "memory_metrics": app.cognitive_memory.metrics,
    }


@router.get("/failures/intelligence")
async def runtime_failure_intelligence(request: Request) -> dict:
    app = request.app.state.odin
    report = await app.failure_intelligence.analyze()
    return report.to_dict()


@router.get("/optimization")
async def runtime_optimization(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "cycles": app.improvement_loop.cycle_count,
        "last_strategy_stats": app.experience_engine.strategy_stats(),
    }


@router.get("/memory-graph")
async def runtime_memory_graph(request: Request, limit: int = 100) -> dict:
    app = request.app.state.odin
    return await app.cognitive_memory.export_snapshot(limit=limit)


@router.get("/strategy-performance")
async def runtime_strategy_performance(request: Request) -> dict:
    app = request.app.state.odin
    return {"strategies": app.experience_engine.strategy_stats()}


@router.get("/capability-performance")
async def runtime_capability_performance(request: Request) -> dict:
    app = request.app.state.odin
    return {"capabilities": app.execution_intelligence.capability_scores()}


@router.post("/learning/recalibrate")
async def runtime_learning_recalibrate(request: Request) -> dict:
    app = request.app.state.odin
    return await app.improvement_loop.recalibrate_confidence()


@router.post("/optimization/run")
async def runtime_optimization_run(request: Request) -> dict:
    app = request.app.state.odin
    return await app.improvement_loop.run_cycle()
