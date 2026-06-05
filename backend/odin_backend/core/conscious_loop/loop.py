"""Runtime conscious loop — perpetual cognitive cycle."""

import asyncio
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.core.bus.signals import Signal, SignalKind, SignalSource
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.core.conscious_loop.decisions import CycleDecision, CycleGovernanceResult
from odin_backend.core.conscious_loop.planner import SelfReasoningPlanner
from odin_backend.core.governor.decisions import ExecutionRequest, GovernorDecisionType
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId, TaskCreate, TaskPriority, TaskStatus
from odin_backend.models.task_graph import TaskNodeStatus
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ConsciousCycleResult(BaseModel):
    tick: int
    decision: CycleDecision
    reason: str
    ingested: int = 0
    ready_nodes: int = 0
    executed: int = 0
    escalations: list[dict[str, Any]] = Field(default_factory=list)
    planning_actions: list[str] = Field(default_factory=list)
    coherence_score: float = 1.0
    duration_ms: float = 0.0


class RuntimeConsciousLoop:
    """
    Continuous cognition: reactive + proactive hybrid.

    Governor remains final gate; stability runs on interval only.
    """

    def __init__(self, app: Any) -> None:
        self._app = app
        self._planner = SelfReasoningPlanner()
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._tick_count = 0
        self._last_cycle: ConsciousCycleResult | None = None
        self._escalation_queue: list[dict[str, Any]] = []

    @property
    def tick_count(self) -> int:
        return self._tick_count

    def last_cycle(self) -> dict[str, Any]:
        return self._last_cycle.model_dump(mode="json") if self._last_cycle else {}

    def pending_escalations(self) -> list[dict[str, Any]]:
        return list(self._escalation_queue)

    async def start(self) -> None:
        settings = self._app.settings
        if not settings.conscious_loop_enabled:
            return
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_forever())
        logger.info(
            "conscious_loop_started",
            interval=settings.conscious_loop_interval_seconds,
        )

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("conscious_loop_stopped")

    async def _run_forever(self) -> None:
        interval = self._app.settings.conscious_loop_interval_seconds
        while self._running:
            try:
                await self.run_cycle()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.exception("conscious_loop_cycle_error", error=str(exc))
            await asyncio.sleep(interval)

    async def run_cycle(self) -> ConsciousCycleResult:
        """Single conscious cycle (10 steps)."""
        import time

        start = time.perf_counter()
        self._tick_count += 1
        app = self._app
        kernel = app.kernel

        # 1 INGEST
        state = kernel.get_state()
        ingested = len(state.active_signals)
        await self._ingest_external_work()
        tick_signal = Signal(
            kind=SignalKind.SYSTEM,
            name="conscious.tick",
            type="system.conscious.tick",
            source=str(AgentId.ODIN),
            source_kind=SignalSource.SYSTEM,
            priority=40,
            payload={"tick": self._tick_count},
        )
        state = await kernel.process_signal(tick_signal)
        ingested += 1

        # 2 INTERPRET — kernel already processed tick; re-read focus
        focus = state.current_focus

        # 3 PRIORITIZE
        ranked = app.priority_engine.rank()
        state.apply_priorities(ranked)
        kernel.commit_state(state)

        # 4 PLAN
        plan = self._planner.refine(kernel.task_graph, focus=focus)
        kernel.apply_planning(plan)
        state = kernel.get_state()

        # 5 COHERENCE
        report = app.coherence.validate(
            state, kernel.recent_signals(30), task_graph=kernel.task_graph
        )
        state.apply_coherence(report)
        kernel.commit_state(state)

        # 6 GOVERNANCE
        ready = kernel.task_graph.ready_nodes()
        governance = self._evaluate_governance(report, ready)
        planning_actions = list(plan.actions)

        executed = 0
        escalations: list[dict[str, Any]] = []

        # 7–8 EXECUTE + OBSERVE
        if governance.decision == CycleDecision.ALLOW:
            executed, exec_results = await self._execute_ready_nodes(ready)
            for res in exec_results:
                if not res.get("success"):
                    escalations.append(res)
        elif governance.decision == CycleDecision.ESCALATE:
            esc = {
                "tick": self._tick_count,
                "reason": governance.reason,
                "coherence": report.model_dump(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            escalations.append(esc)
            self._escalation_queue.append(esc)
            await self._notify_escalation(esc)

        # 9 MEMORY UPDATE
        if executed > 0:
            try:
                await app.memory.save_memory(
                    f"Conscious cycle {self._tick_count}: executed {executed} task(s)",
                    category="outcome",
                    metadata={"tick": self._tick_count, "focus": focus},
                )
            except Exception:
                pass
            await kernel.refresh_memory_context()

        # 10 STABILITY TICK (periodic)
        stability_interval = app.settings.conscious_loop_stability_interval
        if (
            app.settings.stability_loop_enabled
            and stability_interval > 0
            and self._tick_count % stability_interval == 0
        ):
            audit = await app.stability.run_cycle(app)
            kernel.record_stability_check(audit)

        state = kernel.get_state()
        state.task_graph = kernel.task_graph.snapshot()
        kernel.commit_state(state)

        elapsed_ms = (time.perf_counter() - start) * 1000
        result = ConsciousCycleResult(
            tick=self._tick_count,
            decision=governance.decision,
            reason=governance.reason,
            ingested=ingested,
            ready_nodes=len(ready),
            executed=executed,
            escalations=escalations,
            planning_actions=planning_actions,
            coherence_score=report.coherence_score,
            duration_ms=round(elapsed_ms, 2),
        )
        self._last_cycle = result
        await self._emit_tick(result)
        logger.info("conscious_cycle_complete", **result.model_dump())
        return result

    async def _ingest_external_work(self) -> None:
        """Sync queued orchestrator tasks into kernel task graph."""
        app = self._app
        try:
            queued = await app.task_queue.list_tasks(status=TaskStatus.QUEUED, limit=20)
        except Exception:
            queued = []
        for task in queued:
            if app.kernel.task_graph.get(task.id):
                continue
            app.kernel.add_task_node(
                goal=task.description or task.title,
                task_id=task.id,
                assigned_agent=str(task.assigned_agent) if task.assigned_agent else None,
                priority=50,
            )

    def _evaluate_governance(self, report: Any, ready: list) -> CycleGovernanceResult:
        app = self._app
        level = app.autonomy.current_level

        if report.conflict_report:
            return CycleGovernanceResult(
                decision=CycleDecision.ESCALATE,
                reason="Coherence conflicts — execution halted",
                ready_nodes=len(ready),
                explainable={"conflicts": report.conflict_report},
            )

        if app.coherence.blocks_execution():
            return CycleGovernanceResult(
                decision=CycleDecision.DEFER,
                reason=f"Coherence score {report.coherence_score} below threshold",
                ready_nodes=len(ready),
            )

        if level <= 1:
            return CycleGovernanceResult(
                decision=CycleDecision.OBSERVE,
                reason="Autonomy level 1 or below — observation and suggestions only",
                ready_nodes=len(ready),
            )

        if level == 2:
            return CycleGovernanceResult(
                decision=CycleDecision.OBSERVE,
                reason="Autonomy level 2 — task preparation only (planning applied)",
                ready_nodes=len(ready),
            )

        if not ready:
            return CycleGovernanceResult(
                decision=CycleDecision.OBSERVE,
                reason="No ready task nodes — continuous evaluation",
                ready_nodes=0,
            )

        return CycleGovernanceResult(
            decision=CycleDecision.ALLOW,
            reason="Governor path open — controlled execution",
            ready_nodes=len(ready),
        )

    async def _execute_ready_nodes(self, ready: list) -> tuple[int, list[dict[str, Any]]]:
        app = self._app
        max_exec = app.settings.conscious_loop_max_executions_per_cycle
        results: list[dict[str, Any]] = []
        executed = 0

        for node in ready[:max_exec]:
            app.kernel.task_graph.update_status(node.id, TaskNodeStatus.RUNNING)
            tool_name = node.output.get("tool_name")
            params = node.output.get("params", {})

            if tool_name:
                pipeline = await app.execution_contract.run_tool_pipeline(
                    app,
                    ExecutionRequest(
                        tool_name=tool_name,
                        agent_id=node.assigned_agent or "odin",
                        params=params,
                        task_id=node.id,
                        user_confirmed=False,
                    ),
                    skip_stability=True,
                )
                success = pipeline.success
                status = TaskNodeStatus.COMPLETE if success else TaskNodeStatus.FAILED
                app.kernel.task_graph.update_status(
                    node.id, status, output={"pipeline": pipeline.model_dump()}
                )
                results.append({"node_id": node.id, "success": success, "tool": tool_name})
            elif node.assigned_agent:
                try:
                    agent = AgentId(node.assigned_agent)
                except ValueError:
                    agent = None
                create = TaskCreate(
                    title=node.goal[:80],
                    description=node.goal,
                    assigned_agent=agent,
                    priority=TaskPriority.NORMAL,
                    metadata={"conscious_loop": True, "node_id": node.id},
                )
                await app.agent_protocol.submit_orchestrator_task(app.orchestrator, create)
                results.append({"node_id": node.id, "success": True, "delegated": True})
            else:
                # No tool/agent — mark for planning; avoid unsolicited execution
                app.kernel.task_graph.update_status(
                    node.id,
                    TaskNodeStatus.BLOCKED,
                    output={"reason": "missing_tool_and_agent"},
                )
                results.append({"node_id": node.id, "success": False, "skipped": True})
                continue

            executed += 1

        return executed, results

    async def _notify_escalation(self, payload: dict[str, Any]) -> None:
        await self._publish(
            Event(
                type=EventType.CONSCIOUS_LOOP_ESCALATION,
                source=AgentId.ODIN,
                payload=payload,
            )
        )

    async def _emit_tick(self, result: ConsciousCycleResult) -> None:
        await self._publish(
            Event(
                type=EventType.CONSCIOUS_LOOP_TICK,
                source=AgentId.ODIN,
                payload=result.model_dump(mode="json"),
            )
        )

    async def _publish(self, event: Event) -> None:
        bus = self._app.event_bus
        if isinstance(bus, SignalUnificationBus):
            await bus.inner.publish(event)
        else:
            await bus.publish(event)
