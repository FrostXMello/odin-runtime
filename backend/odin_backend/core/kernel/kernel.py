"""ODIN Cognitive Kernel — unified brain; sole CognitiveState write authority."""

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.bus.signals import Signal, SignalKind
from odin_backend.core.context_graph.graph import GlobalContextGraph
from typing import TYPE_CHECKING

from odin_backend.core.kernel.reasoning import KernelReasoningMixin
from odin_backend.core.kernel.state import CognitiveState
from odin_backend.models.task_graph import TaskGraph, TaskNode, TaskNodeStatus

if TYPE_CHECKING:
    from odin_backend.core.coherence.engine import CoherenceEngine
    from odin_backend.core.governor.governor import ExecutionGovernor
from odin_backend.core.priority.engine import CognitivePriorityEngine, PriorityItemKind
from odin_backend.core.bus.unified_bus import SignalUnificationBus
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class OdinCognitiveKernel(KernelReasoningMixin):
    """
    Central intelligence layer.

    Subsystems are signal producers; kernel interprets, prioritizes, and coordinates.
    Only this class commits CognitiveState updates.
    """

    def __init__(
        self,
        event_bus: EventBus,
        context_graph: GlobalContextGraph,
        priority_engine: CognitivePriorityEngine,
        governor: "ExecutionGovernor",
        coherence: "CoherenceEngine | None" = None,
    ) -> None:
        self._event_bus = event_bus
        self._graph = context_graph
        self._priority = priority_engine
        self._governor = governor
        self._coherence = coherence
        self._state = CognitiveState()
        self._signal_buffer: list[Signal] = []
        self._conflict_log: list[str] = []
        self.task_graph = TaskGraph()
        self._autonomy: Any = None
        self._agent_registry: Any = None
        self._memory: Any = None
        self._env_config: Any = None
        self._init_reasoning()

    def set_environment_config(self, env_config: Any) -> None:
        """Kernel reads runtime behavior from environment config only."""
        self._env_config = env_config

    @property
    def env_config(self) -> Any:
        return self._env_config

    def set_runtime_providers(
        self,
        *,
        autonomy: Any = None,
        agent_registry: Any = None,
        memory: Any = None,
    ) -> None:
        self._autonomy = autonomy
        self._agent_registry = agent_registry
        self._memory = memory

    def get_state(self) -> CognitiveState:
        return self._state.model_copy(deep=True)

    def commit_state(self, state: CognitiveState) -> None:
        """Explicit state commit (used by execution contract)."""
        self._state = state

    def recent_signals(self, limit: int = 20) -> list[Signal]:
        return list(self._signal_buffer[-limit:])

    async def process_signal(self, signal: Signal) -> CognitiveState:
        """Interpret signal → graph → priority → coherence → unified state."""
        self._signal_buffer.append(signal)
        if len(self._signal_buffer) > 200:
            self._signal_buffer = self._signal_buffer[-200:]

        self._graph.apply_signal(signal)
        self._priority.ingest_signal(signal)
        self._resolve_conflicts(signal)
        self._apply_task_graph_signal(signal)

        ranked = self._priority.rank()
        self._state.apply_priorities(ranked)

        self._state.active_signals = [s.model_dump(mode="json") for s in self._signal_buffer[-20:]]
        self._state.last_signal = signal.type or signal.name
        self._state.signal_count += 1
        self._state.task_graph = self.task_graph.snapshot()
        self._state.graph_summary = {
            "nodes": self._graph.snapshot().get("node_count", 0),
            "edges": self._graph.snapshot().get("edge_count", 0),
        }
        self._state.active_context = self._build_active_context(signal)
        self._state.recommended_actions = self._extract_recommendations(ranked)
        self._state.execution_decisions = self._governor.recent_decisions(5)
        self._state.system_health = self._assess_health(signal)
        self._state.autonomy_state = self._build_autonomy_state()
        self._state.active_agents = self._build_active_agents()
        self._state.memory_context = await self._build_memory_context()

        if self._coherence:
            report = self._coherence.validate(
                self._state,
                self._signal_buffer[-30:],
                task_graph=self.task_graph,
            )
            self._state.apply_coherence(report)
            self._state.system_health["coherence_score"] = report.coherence_score

        if isinstance(self._event_bus, SignalUnificationBus):
            self._state.apply_runtime_metrics(self._event_bus.runtime_metrics())

        self._apply_mission_metrics()
        self._apply_perception_metrics()

        self._state.updated_at = signal.timestamp

        await self._publish_outbound(
            Event(
                type=EventType.KERNEL_STATE_UPDATED,
                source=AgentId.ODIN,
                correlation_id=signal.correlation_id,
                workflow_id=signal.workflow_id,
                task_id=signal.task_id,
                payload=self._state.model_dump(mode="json"),
            )
        )
        return self._state

    def add_task_node(
        self,
        *,
        goal: str,
        task_id: str | None = None,
        assigned_agent: str | None = None,
        dependencies: list[str] | None = None,
        priority: int = 50,
        input_signal_id: str | None = None,
    ) -> TaskNode:
        from uuid import uuid4

        node = TaskNode(
            id=task_id or str(uuid4()),
            goal=goal,
            dependencies=dependencies or [],
            assigned_agent=assigned_agent,
            priority=priority,
            input_signals=[input_signal_id] if input_signal_id else [],
        )
        self.task_graph.add_node(node)
        self._state.task_graph = self.task_graph.snapshot()
        return node

    def _apply_task_graph_signal(self, signal: Signal) -> None:
        if signal.kind != SignalKind.TASK and signal.kind != SignalKind.WORKFLOW:
            return
        tid = signal.task_id
        if not tid:
            return
        node = self.task_graph.get(tid)
        if not node and "created" in signal.name:
            self.add_task_node(
                goal=signal.payload.get("goal", signal.name),
                task_id=tid,
                assigned_agent=signal.payload.get("assigned_agent"),
                input_signal_id=signal.id,
            )
            return
        if not node:
            return
        if "started" in signal.name or "running" in signal.name:
            self.task_graph.update_status(tid, TaskNodeStatus.RUNNING)
        elif "completed" in signal.name:
            self.task_graph.update_status(
                tid, TaskNodeStatus.COMPLETE, output=signal.payload
            )
        elif "failed" in signal.name:
            self.task_graph.update_status(
                tid, TaskNodeStatus.FAILED, output=signal.payload
            )

    async def _publish_outbound(self, event: Event) -> None:
        if isinstance(self._event_bus, SignalUnificationBus):
            await self._event_bus.inner.publish(event)
        else:
            await self._event_bus.publish(event)

    def _resolve_conflicts(self, signal: Signal) -> None:
        recent_kinds = {s.kind for s in self._signal_buffer[-5:]}
        if SignalKind.WORKFLOW in recent_kinds and SignalKind.RECOMMENDATION in recent_kinds:
            wf = [s for s in self._signal_buffer[-5:] if s.kind == SignalKind.WORKFLOW]
            if any("failed" in s.name for s in wf):
                msg = "Conflict resolved: workflow failure supersedes recommendations"
                if msg not in self._conflict_log:
                    self._conflict_log.append(msg)

    def _build_active_context(self, signal: Signal) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "last_signal_kind": signal.kind.value,
            "last_signal_type": signal.type,
            "last_signal_name": signal.name,
            "source": signal.source,
            "source_kind": signal.source_kind.value,
            "context_refs": signal.context_refs,
        }
        if signal.workflow_id:
            ctx["workflow_id"] = signal.workflow_id
            related = self._graph.related(f"workflow:{signal.workflow_id}", depth=1)
            ctx["related_entities"] = [n.label for n in related[:5]]
        return ctx

    def _build_autonomy_state(self) -> dict[str, Any]:
        if not self._autonomy:
            return {"level": 0, "grants": 0}
        return {
            "level": self._autonomy.current_level,
            "active_grants": len(self._autonomy._active_grants()),  # noqa: SLF001
        }

    def _build_active_agents(self) -> dict[str, Any]:
        if not self._agent_registry:
            return {}
        try:
            agents = self._agent_registry.list_agents()
            return {a: {"status": "registered"} for a in agents}
        except Exception:
            return {}

    async def _build_memory_context(self) -> dict[str, Any]:
        """Return cached memory context; use refresh_memory_context() to update."""
        return self._state.memory_context or {"recent_count": 0}

    async def refresh_memory_context(self, query: str = "recent context", limit: int = 3) -> dict[str, Any]:
        if not self._memory:
            ctx = {"recent_count": 0}
        else:
            try:
                results = await self._memory.retrieval.search(query, limit=limit)
                ctx = {
                    "recent_count": len(results),
                    "snippets": [str(r.get("content", r))[:80] for r in results[:3]],
                }
            except Exception:
                ctx = {"recent_count": 0}
        self._state.memory_context = ctx
        return ctx

    def _extract_recommendations(self, ranked: list) -> list[dict[str, Any]]:
        return [
            i.model_dump(mode="json")
            for i in ranked
            if i.kind == PriorityItemKind.RECOMMENDATION
        ][:5]

    def _assess_health(self, signal: Signal) -> dict[str, Any]:
        degraded = signal.kind == SignalKind.SECURITY or "failed" in signal.name
        recent_failures = sum(
            1
            for s in self._signal_buffer[-20:]
            if "failed" in s.name or s.kind == SignalKind.SECURITY
        )
        blocked = sum(
            1
            for n in self.task_graph.nodes.values()
            if n.status == TaskNodeStatus.BLOCKED
        )
        return {
            "status": "degraded" if degraded or recent_failures >= 3 else "healthy",
            "degraded": degraded or recent_failures >= 3,
            "recent_failure_signals": recent_failures,
            "blocked_task_nodes": blocked,
        }

    def apply_planning(self, report: Any) -> None:
        """Apply self-reasoning planner output (kernel-owned task graph)."""
        for node in report.new_nodes:
            self.task_graph.add_node(node)
        for node_id, priority in report.priority_adjustments.items():
            existing = self.task_graph.get(node_id)
            if existing:
                existing.priority = priority
        self._state.task_graph = self.task_graph.snapshot()
        if report.actions:
            self._state.recommended_actions = [
                *self._state.recommended_actions,
                *[{"action": a} for a in report.actions[:5]],
            ][-10:]

    def _apply_mission_metrics(self) -> None:
        mgr = getattr(self, "_mission_manager", None)
        runtime = getattr(self, "_mission_runtime", None)
        if not mgr:
            return
        active = []
        failures = 0
        checkpoints = 0
        focus: str | None = None
        for m in mgr._active.values():  # noqa: SLF001
            if m.is_terminal():
                failures += 1 if m.current_state.value == "failed" else 0
                continue
            active.append(
                {
                    "mission_id": m.mission_id,
                    "state": m.current_state.value,
                    "objective": m.objective[:80],
                }
            )
            if not focus:
                focus = m.objective[:120]
            checkpoints += len(m.checkpoints)
        rt_metrics = runtime.metrics if runtime else {}
        self._state.apply_mission_metrics(
            {
                "active_missions": active[:10],
                "mission_execution_rate": float(rt_metrics.get("waves_executed", 0)),
                "mission_failures": failures + int(rt_metrics.get("tasks_failed", 0)),
                "mission_retries": int(rt_metrics.get("retries", 0)),
                "mission_checkpoint_count": checkpoints,
                "long_horizon_focus": focus,
            }
        )

    def set_mission_providers(self, *, manager: Any = None, runtime: Any = None) -> None:
        self._mission_manager = manager
        self._mission_runtime = runtime

    def set_perception_providers(
        self,
        *,
        perception: Any = None,
        confidence: Any = None,
        perception_memory: Any = None,
    ) -> None:
        self._perception = perception
        self._confidence = confidence
        self._perception_memory = perception_memory

    def _apply_perception_metrics(self) -> None:
        perception = getattr(self, "_perception", None)
        confidence = getattr(self, "_confidence", None)
        memory = getattr(self, "_perception_memory", None)
        runtime = getattr(self, "_mission_runtime", None)
        if not perception:
            return
        snap = confidence.global_snapshot if confidence else None
        adaptive: list[dict] = []
        mgr = getattr(self, "_mission_manager", None)
        if mgr:
            for m in list(mgr._active.values())[:5]:  # noqa: SLF001
                adaptive.extend(m.adaptation_log[-3:])

        self._state.apply_perception_metrics(
            {
                "environment_awareness": {
                    "system_health": self._state.system_health,
                    "runtime_loop_health": self._state.runtime_loop_health,
                    "live_perception_count": len(perception.live_perceptions),
                },
                "active_perceptions": [
                    p.model_dump(mode="json") for p in perception.live_perceptions[-10:]
                ],
                "adaptive_actions": adaptive[-10:],
                "failure_patterns": memory.failure_patterns() if memory else {},
                "confidence_score": snap.aggregate if snap else 1.0,
                "mission_stability_score": snap.mission_stability if snap else 1.0,
                "execution_recovery_rate": (
                    runtime.metrics.get("execution_recovery_rate", 1.0) if runtime else 1.0
                ),
            }
        )

    def record_stability_check(self, audit: dict[str, Any]) -> None:
        self._state.last_stability_check = datetime.now(timezone.utc)
        self._state.system_health["last_stability_run"] = audit.get("run")

    def explain(self) -> dict[str, Any]:
        return {
            "role": "ODIN Cognitive Kernel",
            "signal_count": self._state.signal_count,
            "conflicts_resolved": self._conflict_log[-5:],
            "current_focus": self._state.current_focus,
            "task_graph_nodes": len(self.task_graph.nodes),
            "architecture": (
                "signal → kernel → priority → coherence → governor → autonomy → "
                "execution → memory → stability"
            ),
        }
