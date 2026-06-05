"""Live execution loop — end-to-end signal → execution → memory."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.bus.signals import Signal, SignalKind, SignalSource
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.core.execution_gate.gate import GateDecision
from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType
from odin_backend.core.model_router.router import TaskModelType
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class LiveCycleResult(BaseModel):
    success: bool
    objective: str = ""
    model_used: str | None = None
    coherence_score: float = 1.0
    governor_decision: str = ""
    execution_trace: list[dict[str, Any]] = Field(default_factory=list)
    memory_updated: bool = False
    graph_updated: bool = False
    stability_ran: bool = False


class LiveExecutionLoop:
    """Heart of ODIN runtime — full 12-step cognitive cycle."""

    def __init__(self, app: Any) -> None:
        self._app = app
        self._tick = 0
        self._running = False
        self._task: Any = None

    async def start(self) -> None:
        if not self._app.settings.live_loop_enabled:
            return
        if self._running:
            return
        self._running = True
        import asyncio

        self._task = asyncio.create_task(self._run_forever())
        logger.info("live_execution_loop_started")

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except Exception:
                pass
        logger.info("live_execution_loop_stopped")

    async def _run_forever(self) -> None:
        import asyncio

        interval = self._app.settings.live_loop_interval_seconds
        while self._running:
            try:
                await self.run_full_cycle()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("live_loop_error", error=str(exc))
            await asyncio.sleep(interval)

    async def run_full_cycle(
        self,
        *,
        objective: str | None = None,
        fast_path: bool = False,
    ) -> LiveCycleResult:
        """Execute complete live cognitive cycle."""
        self._tick += 1
        app = self._app
        kernel = app.kernel
        trace: list[dict[str, Any]] = []
        obj = objective or "Continuous system evaluation"

        def step(name: str, detail: dict) -> None:
            trace.append({"step": name, **detail})
            kernel._state.append_execution_step(name, detail)

        # 1 ingest
        state = kernel.get_state()
        signals = list(state.active_signals)
        if objective:
            user_signal = Signal(
                kind=SignalKind.CONVERSATION,
                name="conversation.message",
                type="user.objective",
                source="user",
                source_kind=SignalSource.USER,
                priority=85,
                payload={"text": objective, "objective": objective},
                requires_response=True,
            )
            await kernel.process_signal(user_signal)
            signals.append(user_signal.model_dump(mode="json"))
        step("ingest_signals", {"count": len(signals)})

        # 2 kernel interpret
        tick = Signal(
            kind=SignalKind.SYSTEM,
            name="live.loop.tick",
            type="system.live.tick",
            source=str(AgentId.ODIN),
            source_kind=SignalSource.SYSTEM,
            payload={"tick": self._tick, "fast_path": fast_path},
        )
        state = await kernel.process_signal(tick)
        step("kernel_interpret", {"focus": state.current_focus})

        # 3 prioritize
        ranked = app.priority_engine.rank()
        state.apply_priorities(ranked)
        kernel.commit_state(state)
        step("priority_evaluate", {"ranked": len(ranked)})

        # 4 coherence
        report = app.coherence.validate(state, kernel.recent_signals(30), task_graph=kernel.task_graph)
        state.apply_coherence(report)
        kernel.commit_state(state)
        step("coherence_validate", {"score": report.coherence_score})

        if report.conflict_report:
            kernel._record_live_mind(decision_path=["coherence", "escalate"])
            await self._emit(EventType.LIVE_CYCLE_ESCALATION, {"conflicts": report.conflict_report})
            return LiveCycleResult(
                success=False,
                objective=obj,
                coherence_score=report.coherence_score,
                governor_decision="escalate",
                execution_trace=trace,
            )

        # 5 governor preview for cycle
        gov = await app.governor.evaluate(
            ExecutionRequest(tool_name="get_system_info", agent_id="odin", params={}),
            cognitive_state=state,
        )
        step("governor_decide", {"decision": gov.decision.value})
        kernel._record_live_mind(decision_path=["governor", gov.decision.value])

        if gov.decision not in (GovernorDecisionType.APPROVE,):
            if gov.decision == GovernorDecisionType.ESCALATE_TO_USER:
                return LiveCycleResult(
                    success=False,
                    objective=obj,
                    coherence_score=report.coherence_score,
                    governor_decision=gov.decision.value,
                    execution_trace=trace,
                )

        # 6 autonomy scope
        allowed, reason, _ = app.autonomy.allows_execution(
            ExecutionRequest(tool_name="summarize_content", agent_id="odin", params={"text": obj})
        )
        step("autonomy_scope", {"allowed": allowed, "reason": reason})

        # 7 model router plan
        model_used = "rule-based"
        if objective and app.autonomy.current_level >= 2:
            ctx = state.model_dump_json() if hasattr(state, "model_dump_json") else state.current_focus
            plan, plan_trace = await kernel.execute_llm_planning(objective, context=ctx)
            model_used = plan_trace.get("model_choice", "rule-based")
            kernel._record_live_mind(
                reasoning_trace=plan_trace,
                model_used=model_used,
                decision_path=["model_router", "plan"],
            )
            step("model_router_plan", {"model": model_used, "steps": len(plan.steps)})
        else:
            routing = await app.model_router.route_and_complete(
                [
                    {"role": "system", "content": "You are ODIN cognitive kernel."},
                    {"role": "user", "content": obj},
                ],
                TaskModelType.SUMMARIZATION,
            )
            model_used = routing.model_choice
            kernel._record_live_mind(model_used=model_used, decision_path=["model_router", "summarize"])
            step("model_router_plan", {"model": model_used, "confidence": routing.confidence_score})

        # 11 execution gate validation
        gate_req = ExecutionRequest(
            tool_name="get_system_info",
            agent_id="odin",
            params={},
        )
        gate = app.execution_gate.validate(app, gate_req)
        kernel._state.execution_gate_decision = gate.decision.value
        kernel._state.environment_snapshot = app.env_config.snapshot()
        step("execution_gate_validation", {"decision": gate.decision.value, "reason": gate.reason})

        # 12 valkyrie execution dispatch
        executed = False
        if (
            allowed
            and gov.decision == GovernorDecisionType.APPROVE
            and gate.decision == GateDecision.ALLOW
            and app.env_config.valkyrie_enabled
            and app.autonomy.current_level >= 3
        ):
            vk = await app.valkyrie.execute_task(tool_name="get_system_info", params={})
            executed = vk.success
            kernel._state.valkyrie_action_trace = vk.valkyrie_trace
            step(
                "valkyrie_execution_dispatch",
                {
                    "success": vk.success,
                    "trace_id": vk.execution_trace_id,
                    "gate": vk.gate_decision,
                },
            )
            if objective:
                sum_vk = await app.valkyrie.execute_task(
                    tool_name="summarize_content",
                    params={"text": f"Objective: {objective}. State focus: {state.current_focus}"},
                )
                step("valkyrie_summarization", {"success": sum_vk.success})
        elif allowed and gov.decision == GovernorDecisionType.APPROVE and app.autonomy.current_level >= 3:
            pipeline = await app.live_tools.execute_with_trace(
                app, "get_system_info", {}, agent_id="mimir"
            )
            executed = pipeline.get("success", False)
            step("tool_execution_readonly", {"success": executed, "tool": "get_system_info"})
            if objective:
                sum_p = await app.live_tools.execute_with_trace(
                    app,
                    "summarize_content",
                    {"text": f"Objective: {objective}. State focus: {state.current_focus}"},
                    agent_id="munin",
                )
                step("agent_summarization", {"success": sum_p.get("success", False)})

        # 10 memory update
        memory_updated = False
        try:
            mem_id = await app.memory.save_memory(
                f"Live cycle {self._tick}: {obj[:200]}",
                category="outcome",
                metadata={"model": model_used, "tick": self._tick},
            )
            kernel._state.memory_delta = {"memory_id": mem_id, "action": "saved"}
            memory_updated = True
            step("memory_update", {"memory_id": mem_id})
        except Exception as exc:
            step("memory_update", {"error": str(exc)})

        # 11 graph update
        before = state.graph_summary.get("nodes", 0)
        state = await kernel.process_signal(
            Signal(
                kind=SignalKind.MEMORY,
                name="memory.updated",
                type="memory.updated",
                source="mimir",
                payload={"memory_id": "live-cycle", "category": "outcome"},
            )
        )
        after = state.graph_summary.get("nodes", 0)
        kernel._state.graph_delta = {"nodes_before": before, "nodes_after": after}
        step("graph_update", {"nodes": after})

        # 12 stability tick
        stability_ran = False
        interval = app.settings.live_loop_stability_interval
        if app.settings.stability_loop_enabled and interval > 0 and self._tick % interval == 0:
            await app.stability.run_cycle(app)
            stability_ran = True
            step("stability_tick", {"tick": self._tick})

        kernel.commit_state(kernel.get_state())
        await self._emit(
            EventType.LIVE_CYCLE_COMPLETED,
            {
                "tick": self._tick,
                "model_used": model_used,
                "coherence_score": report.coherence_score,
                "trace_steps": len(trace),
            },
        )

        return LiveCycleResult(
            success=True,
            objective=obj,
            model_used=model_used,
            coherence_score=report.coherence_score,
            governor_decision=gov.decision.value,
            execution_trace=trace,
            memory_updated=memory_updated,
            graph_updated=after != before,
            stability_ran=stability_ran,
        )

    async def run_cognitive_cycle(self, user_input: str) -> LiveCycleResult:
        """Fast-path triggered cycle for explicit user objectives."""
        return await self.run_full_cycle(objective=user_input, fast_path=True)

    async def _emit(self, event_type: EventType, payload: dict) -> None:
        bus = self._app.event_bus
        event = Event(type=event_type, source=AgentId.ODIN, payload=payload)
        if isinstance(bus, SignalUnificationBus):
            await bus.inner.publish(event)
        else:
            await bus.publish(event)
