"""Self-development loop APIs (Prompt 42)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["self-evolution-runtime"])


class CycleRequest(BaseModel):
    metrics: dict = Field(default_factory=dict)


class PipelineRequest(BaseModel):
    goal: str
    files: list[str] = Field(default_factory=list)
    diff: str = ""


class RollbackRequest(BaseModel):
    branch: str


class ApproveRequest(BaseModel):
    audit_id: str
    operator: str = "default"


class LearnRequest(BaseModel):
    outcome: str
    benchmark_delta: float = 0.0


class DecisionRequest(BaseModel):
    title: str
    rationale: str


class ReviewRequest(BaseModel):
    proposal: dict = Field(default_factory=dict)
    level: str | None = None


@router.get("/self-evolution")
async def runtime_self_evolution(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "evolution": app.self_evolution.snapshot(),
        "governance": app.evolution_governance.snapshot(),
        "memory": app.self_improvement_memory.snapshot(),
    }


@router.post("/self-evolution/cycle")
async def runtime_self_evolution_cycle(body: CycleRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_evolution.run_cycle(metrics=body.metrics or None)


@router.post("/self-evolution/learn")
async def runtime_self_evolution_learn(body: LearnRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_evolution.learn(outcome=body.outcome, benchmark_delta=body.benchmark_delta)


@router.get("/improvements")
async def runtime_improvements(request: Request) -> dict:
    app = request.app.state.odin
    return {"backlog": app.self_evolution.snapshot().get("backlog", [])}


@router.get("/benchmarks")
async def runtime_benchmarks(request: Request) -> dict:
    app = request.app.state.odin
    return {"benchmarks": app.runtime_benchmarks.snapshot()}


@router.post("/benchmarks/run")
async def runtime_benchmarks_run(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_benchmarks.run_suite()


@router.get("/benchmarks/history")
async def runtime_benchmarks_history(request: Request) -> dict:
    app = request.app.state.odin
    return await app.runtime_benchmarks.history()


@router.get("/upgrades")
async def runtime_upgrades(request: Request) -> dict:
    app = request.app.state.odin
    return {"evolution": app.self_evolution.snapshot(), "governance": app.evolution_governance.snapshot()}


@router.post("/upgrades/review")
async def runtime_upgrades_review(body: ReviewRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_governance.review(proposal=body.proposal, level=body.level)


@router.post("/upgrades/approve")
async def runtime_upgrades_approve(body: ApproveRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_governance.approve(audit_id=body.audit_id, operator=body.operator)


@router.get("/regressions")
async def runtime_regressions(request: Request) -> dict:
    app = request.app.state.odin
    history = await app.runtime_benchmarks.history()
    return {"history": history.get("history", []), "memory": app.self_improvement_memory.snapshot()}


@router.get("/upgrade-cycles")
async def runtime_upgrade_cycles(request: Request) -> dict:
    app = request.app.state.odin
    return {"evolution": app.self_evolution.snapshot()}


@router.get("/architecture")
async def runtime_architecture_timeline(request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_improvement_memory.architecture_timeline()


@router.post("/architecture/decision")
async def runtime_architecture_decision(body: DecisionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_improvement_memory.record_decision(title=body.title, rationale=body.rationale)


@router.get("/architecture-history")
async def runtime_architecture_history(request: Request) -> dict:
    app = request.app.state.odin
    return await app.self_improvement_memory.architecture_timeline()


@router.get("/performance-drift")
async def runtime_performance_drift(request: Request) -> dict:
    app = request.app.state.odin
    hist = await app.runtime_benchmarks.history()
    return {"drift": hist, "benchmarks": app.runtime_benchmarks.snapshot()}


@router.get("/patch-pipeline")
async def runtime_patch_pipeline(request: Request) -> dict:
    app = request.app.state.odin
    return {"pipeline": app.autonomous_patching.snapshot(), "patching": app.patching.snapshot()}


@router.post("/patch-pipeline/run")
async def runtime_patch_pipeline_run(body: PipelineRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_patching.pipeline(goal=body.goal, files=body.files, diff=body.diff)


@router.post("/patch-pipeline/rollback")
async def runtime_patch_pipeline_rollback(body: RollbackRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_patching.rollback(branch=body.branch)
