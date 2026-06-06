"""Unified cognitive operating environment APIs (Prompt 46)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["unified-cognitive-runtime"])


class ModeRequest(BaseModel):
    mode: str


class ProfileRequest(BaseModel):
    profile: str


class CommandRequest(BaseModel):
    query: str


class ReasoningRequest(BaseModel):
    thought: str = ""
    branch_b: str = ""


class PresenceConnectRequest(BaseModel):
    thread_id: str = ""


class TurnRequest(BaseModel):
    text: str
    energy: float = 0.6


class RollbackRequest(BaseModel):
    target: str = "last_stable"


class DecisionRequest(BaseModel):
    action: str
    proposal_id: str = "latest"


class DaemonTickRequest(BaseModel):
    idle_s: float = 0.0


class FocusRequest(BaseModel):
    minutes: int = 25


class DistractionRequest(BaseModel):
    context_switches: int = 1


@router.get("/cognitive-workspace")
async def runtime_cognitive_workspace(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_workspace": app.cognitive_workspace.snapshot()}


@router.post("/cognitive-workspace/open")
async def runtime_cognitive_workspace_open(body: ModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_workspace.open(mode=body.mode)


@router.post("/cognitive-workspace/mode")
async def runtime_cognitive_workspace_mode(body: ModeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_workspace.set_mode(body.mode)


@router.post("/cognitive-workspace/profile")
async def runtime_cognitive_workspace_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_workspace.set_profile(body.profile)


@router.post("/cognitive-workspace/command")
async def runtime_cognitive_workspace_command(body: CommandRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_workspace.quick_command(query=body.query)


@router.get("/reasoning-live")
async def runtime_reasoning_live(request: Request) -> dict:
    app = request.app.state.odin
    return {"live_reasoning": app.live_reasoning.snapshot()}


@router.post("/reasoning-live/render")
async def runtime_reasoning_live_render(body: ReasoningRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_reasoning.render(thought=body.thought, branch_b=body.branch_b)


@router.post("/reasoning-live/profile")
async def runtime_reasoning_live_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.live_reasoning.set_profile(body.profile)


@router.get("/conversational-presence")
async def runtime_conversational_presence(request: Request) -> dict:
    app = request.app.state.odin
    return {"conversational_presence": app.conversational_presence.snapshot()}


@router.post("/conversational-presence/connect")
async def runtime_conversational_presence_connect(body: PresenceConnectRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversational_presence.connect(thread_id=body.thread_id)


@router.post("/conversational-presence/turn")
async def runtime_conversational_presence_turn(body: TurnRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversational_presence.turn(text=body.text, energy=body.energy)


@router.post("/conversational-presence/interrupt")
async def runtime_conversational_presence_interrupt(request: Request) -> dict:
    app = request.app.state.odin
    return await app.conversational_presence.interrupt()


@router.get("/evolution-review")
async def runtime_evolution_review(request: Request) -> dict:
    app = request.app.state.odin
    return {"evolution_review": app.evolution_review.snapshot()}


@router.post("/evolution-review/open")
async def runtime_evolution_review_open(request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_review.open_review()


@router.post("/evolution-review/benchmarks")
async def runtime_evolution_review_benchmarks(request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_review.compare_benchmarks()


@router.post("/evolution-review/rollback")
async def runtime_evolution_review_rollback(body: RollbackRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_review.simulate_rollback(target=body.target)


@router.post("/evolution-review/decide")
async def runtime_evolution_review_decide(body: DecisionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.evolution_review.decide(action=body.action, proposal_id=body.proposal_id)


@router.get("/cognitive-daemon")
async def runtime_cognitive_daemon(request: Request) -> dict:
    app = request.app.state.odin
    return {"cognitive_daemon": app.cognitive_daemon.snapshot()}


@router.post("/cognitive-daemon/tick")
async def runtime_cognitive_daemon_tick(body: DaemonTickRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon.tick(idle_s=body.idle_s)


@router.post("/cognitive-daemon/profile")
async def runtime_cognitive_daemon_profile(body: ProfileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.cognitive_daemon.set_profile(body.profile)


@router.get("/operator-productivity")
async def runtime_operator_productivity(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_productivity": app.operator_productivity.snapshot()}


@router.post("/operator-productivity/focus")
async def runtime_operator_productivity_focus(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_productivity.start_focus(minutes=body.minutes)


@router.post("/operator-productivity/distraction")
async def runtime_operator_productivity_distraction(body: DistractionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_productivity.record_distraction(context_switches=body.context_switches)


@router.get("/operator-productivity/summary")
async def runtime_operator_productivity_summary(request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_productivity.summary()
