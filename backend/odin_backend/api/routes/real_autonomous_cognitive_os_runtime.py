"""Real autonomous cognitive OS APIs (Prompt 50)."""

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/runtime", tags=["real-autonomous-cognitive-os-runtime"])


class WindowRequest(BaseModel):
    window: str = "Odin"


class NotifyRequest(BaseModel):
    title: str
    body: str = ""


class IntentRequest(BaseModel):
    intent: str
    payload: str = ""


class FileRequest(BaseModel):
    path: str


class GoalRequest(BaseModel):
    goal: str


class HorizonRequest(BaseModel):
    days: int = 3


class TaskRequest(BaseModel):
    task: str


class IdleRequest(BaseModel):
    idle_s: float = 0.0


class ReposRequest(BaseModel):
    repos: list[str] = Field(default_factory=lambda: ["local"])


class PatchRequest(BaseModel):
    patch: str = ""


class ScopeRequest(BaseModel):
    scope: str = ""


class ChangeRequest(BaseModel):
    change: str = ""


class LinkRequest(BaseModel):
    topic: str
    prior: str = ""


class SessionRequest(BaseModel):
    session: str = "default"


class TokensRequest(BaseModel):
    tokens: int = 4096


class AgeRequest(BaseModel):
    age_days: int = 45


class ProductivityRequest(BaseModel):
    hours: float = 4.0
    context: str = "engineering"


class FocusRequest(BaseModel):
    minutes: int = 45


@router.get("/native-os")
async def runtime_native_os(request: Request) -> dict:
    app = request.app.state.odin
    return {"native_os": app.native_os.snapshot(), "system_intents": app.system_intents.snapshot()}


@router.post("/native-os/observe")
async def runtime_native_os_observe(body: WindowRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_os.observe_desktop(window=body.window)


@router.post("/native-os/tray")
async def runtime_native_os_tray(request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_os.show_tray()


@router.get("/window-state")
async def runtime_window_state(request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_os.window_state()


@router.post("/notifications/send")
async def runtime_notifications(body: NotifyRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.native_os.notify(title=body.title, body=body.body)


@router.get("/system-intents")
async def runtime_system_intents(request: Request) -> dict:
    app = request.app.state.odin
    return {"system_intents": app.system_intents.snapshot()}


@router.post("/system-intents/dispatch")
async def runtime_system_intents_dispatch(body: IntentRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.system_intents.dispatch(intent=body.intent, payload=body.payload)


@router.post("/system-intents/open-file")
async def runtime_system_intents_open(body: FileRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.system_intents.open_file(path=body.path)


@router.get("/autonomous-loop-v2")
async def runtime_autonomous_loop_v2(request: Request) -> dict:
    app = request.app.state.odin
    return {"autonomous_loop_v2": app.autonomous_loop_v2.snapshot()}


@router.post("/autonomous-loop-v2/resume-goal")
async def runtime_autonomous_loop_resume(body: GoalRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_loop_v2.resume_goal(goal=body.goal)


@router.post("/long-horizon-planning/plan")
async def runtime_long_horizon_plan(body: HorizonRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_loop_v2.plan_horizon(days=body.days)


@router.post("/autonomous-loop-v2/defer")
async def runtime_autonomous_loop_defer(body: TaskRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_loop_v2.defer_task(task=body.task)


@router.post("/autonomous-loop-v2/tick")
async def runtime_autonomous_loop_tick(body: IdleRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.autonomous_loop_v2.autonomous_tick(idle_s=body.idle_s)


@router.get("/engineering-evolution-v2")
async def runtime_engineering_evolution_v2(request: Request) -> dict:
    app = request.app.state.odin
    return {"engineering_evolution_v2": app.engineering_evolution_v2.snapshot()}


@router.post("/multi-repo/reason")
async def runtime_multi_repo(body: ReposRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution_v2.analyze_multi_repo(repos=body.repos)


@router.post("/regression-forecast/forecast")
async def runtime_regression_forecast(body: ChangeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution_v2.forecast_regression(change=body.change)


@router.post("/engineering-evolution-v2/evaluate-patch")
async def runtime_evaluate_patch(body: PatchRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution_v2.evaluate_patch(patch=body.patch)


@router.post("/engineering-evolution-v2/simulate-refactor")
async def runtime_simulate_refactor(body: ScopeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.engineering_evolution_v2.simulate_refactor(scope=body.scope)


@router.get("/memory-fabric-v2")
async def runtime_memory_fabric_v2(request: Request) -> dict:
    app = request.app.state.odin
    return {"memory_fabric_v2": app.memory_fabric_v2.snapshot()}


@router.post("/memory-fabric-v2/link")
async def runtime_memory_fabric_link(body: LinkRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric_v2.link_semantic(topic=body.topic, prior=body.prior)


@router.post("/context-rehydration/rehydrate")
async def runtime_context_rehydration(body: SessionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric_v2.rehydrate_context(session=body.session)


@router.post("/memory-fabric-v2/compress")
async def runtime_memory_fabric_compress(body: TokensRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric_v2.compress_history(tokens=body.tokens)


@router.post("/memory-fabric-v2/replay")
async def runtime_memory_fabric_replay(body: SessionRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric_v2.replay_session(session=body.session)


@router.post("/memory-fabric-v2/prune")
async def runtime_memory_fabric_prune(body: AgeRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.memory_fabric_v2.prune_memory(age_days=body.age_days)


@router.get("/operator-intelligence-v3")
async def runtime_operator_intelligence_v3(request: Request) -> dict:
    app = request.app.state.odin
    return {"operator_intelligence_v3": app.operator_intelligence_v3.snapshot()}


@router.post("/operator-intelligence-v3/optimize")
async def runtime_operator_intelligence_v3_optimize(body: ProductivityRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v3.optimize(hours=body.hours, context=body.context)


@router.post("/deep-focus/start")
async def runtime_deep_focus(body: FocusRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v3.start_deep_focus(minutes=body.minutes)


@router.post("/burnout-awareness/assess")
async def runtime_burnout_awareness(body: ProductivityRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v3.optimize(hours=body.hours, context=body.context)


@router.post("/workflow-mentor/recommend")
async def runtime_workflow_mentor(body: ProductivityRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v3.optimize(hours=body.hours, context=body.context)


@router.post("/cognitive-recovery/plan")
async def runtime_cognitive_recovery(body: ProductivityRequest, request: Request) -> dict:
    app = request.app.state.odin
    return await app.operator_intelligence_v3.optimize(hours=body.hours, context=body.context)


@router.get("/autonomous-activity")
async def runtime_autonomous_activity(request: Request) -> dict:
    app = request.app.state.odin
    return {
        "autonomous_loop_v2": app.autonomous_loop_v2.snapshot(),
        "native_os": app.native_os.snapshot(),
        "engineering_evolution_v2": app.engineering_evolution_v2.snapshot(),
    }


@router.get("/reasoning-pulse")
async def runtime_reasoning_pulse(request: Request) -> dict:
    app = request.app.state.odin
    pulse = {"active": True, "bounded": True}
    if hasattr(app, "cognitive_streams"):
        pulse["streams"] = True
    return {"accepted": True, "pulse": pulse}
