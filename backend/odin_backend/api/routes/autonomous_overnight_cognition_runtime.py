"""Autonomous overnight cognition APIs (Prompt 53)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["autonomous-overnight-cognition-runtime"])


class ModeRequest(BaseModel):
    mode: str = "balanced"


class ThoughtRequest(BaseModel):
    thought: str
    chain: list[str] = Field(default_factory=list)


class ProjectRequest(BaseModel):
    project: str = "local"


class ReposRequest(BaseModel):
    repos: list[str] = Field(default_factory=lambda: ["local"])


class ChangeRequest(BaseModel):
    change: str = ""


class RepoRequest(BaseModel):
    repo: str = "local"


@router.get("/overnight")
async def overnight_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"overnight_cognition": app.overnight_cognition.snapshot()}


@router.post("/overnight/start")
async def overnight_start(request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.start_overnight_cycle()


@router.post("/overnight/pause")
async def overnight_pause(request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.pause_overnight_cycle()


@router.post("/overnight/idle-reasoning")
async def overnight_idle_reasoning(request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.execute_idle_reasoning()


@router.get("/overnight/summary")
async def overnight_summary(request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.generate_overnight_summary()


@router.post("/overnight/resume-state")
async def overnight_resume_state(request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.prepare_resume_state()


@router.post("/overnight/mode")
async def overnight_mode(body: ModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.set_mode(body.mode)


@router.get("/deferred-reasoning")
async def deferred_reasoning_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"deferred_reasoning": app.deferred_reasoning.snapshot()}


@router.post("/deferred-reasoning/defer")
async def deferred_reasoning_defer(body: ThoughtRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.deferred_reasoning.defer_reasoning(thought=body.thought, chain=body.chain)


@router.post("/deferred-reasoning/restore")
async def deferred_reasoning_restore(request: Request) -> dict:
    app = request.app.state.odin
    return await app.deferred_reasoning.restore_reasoning()


@router.post("/deferred-reasoning/replay")
async def deferred_reasoning_replay(body: ThoughtRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.deferred_reasoning.replay_reasoning_context(thought=body.thought)


@router.get("/continuity-forecast")
async def continuity_forecast(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuity_forecasting.generate_continuity_plan()


@router.get("/continuity-forecast/focus")
async def continuity_forecast_focus(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuity_forecasting.forecast_operator_focus()


@router.get("/continuity-forecast/abandoned")
async def continuity_forecast_abandoned(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuity_forecasting.detect_abandoned_work()


@router.get("/morning-briefing")
async def morning_briefing(request: Request) -> dict:
    app = request.app.state.odin
    return await app.morning_briefing.build_morning_briefing()


@router.get("/morning-briefing/overnight")
async def morning_briefing_overnight(request: Request) -> dict:
    app = request.app.state.odin
    return await app.morning_briefing.summarize_overnight_activity()


@router.get("/morning-briefing/focus-plan")
async def morning_briefing_focus_plan(request: Request) -> dict:
    app = request.app.state.odin
    return await app.morning_briefing.generate_focus_plan()


@router.get("/cognitive-maintenance")
async def cognitive_maintenance_status(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_maintenance": app.cognitive_maintenance.snapshot()}


@router.post("/cognitive-maintenance/compact")
async def cognitive_maintenance_compact(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_maintenance.compact_memory_threads()


@router.post("/cognitive-maintenance/stabilize")
async def cognitive_maintenance_stabilize(request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_maintenance.stabilize_runtime_state()


@router.get("/idle-engineering/report")
async def idle_engineering_report(request: Request) -> dict:
    app = request.app.state.odin
    return await app.idle_engineering.prepare_engineering_report()


@router.post("/idle-engineering/analyze")
async def idle_engineering_analyze(body: ReposRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.idle_engineering.analyze_idle_repositories(repos=body.repos)


@router.post("/idle-engineering/regression")
async def idle_engineering_regression(body: ChangeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.idle_engineering.simulate_regression_risk(change=body.change)


@router.get("/unfinished-work")
async def unfinished_work(request: Request) -> dict:
    app = request.app.state.odin
    return await app.continuity_forecasting.detect_abandoned_work()


@router.get("/reasoning-recovery")
async def reasoning_recovery(request: Request) -> dict:
    app = request.app.state.odin
    return await app.deferred_reasoning.restore_reasoning()


@router.get("/repo-drift")
async def repo_drift(request: Request, repo: str = "local") -> dict:
    app = request.app.state.odin
    return await app.idle_engineering.detect_refactor_candidates(repo=repo)


@router.get("/overnight-summary")
async def overnight_summary_alias(request: Request) -> dict:
    app = request.app.state.odin
    return await app.overnight_cognition.generate_overnight_summary()
