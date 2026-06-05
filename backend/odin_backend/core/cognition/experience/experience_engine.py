"""Experience engine — learns from executions and missions."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.experience.execution_scoring import execution_fingerprint, score_execution
from odin_backend.core.cognition.experience.mission_retrospective import build_retrospective
from odin_backend.core.cognition.experience.outcome_analysis import analyze_outcomes
from odin_backend.core.cognition.experience.pattern_mining import mine_failure_clusters, mine_tool_chains
from odin_backend.core.cognition.experience.strategy_learning import update_strategy_stats
from odin_backend.core.cognition.procedural_memory import procedural_from_strategy
from odin_backend.core.cognition.semantic_memory import semantic_from_pattern
from odin_backend.models.mission import Mission
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ExperienceEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._events: list[dict[str, Any]] = []
        self._strategy_stats: dict[str, dict[str, float]] = {}
        self._fingerprints: dict[str, float] = {}
        self._metrics: dict[str, int] = {
            "outcomes_recorded": 0,
            "retrospectives": 0,
            "patterns_mined": 0,
        }

    @property
    def metrics(self) -> dict[str, int]:
        return dict(self._metrics)

    def record_outcome(
        self,
        *,
        mission_id: str,
        task_id: str | None,
        execution_id: str | None,
        capability: str,
        tool: str | None,
        success: bool,
        latency_ms: float | None = None,
        reason: str = "",
    ) -> None:
        fp = execution_fingerprint(capability=capability, tool=tool, mission_id=mission_id)
        score = score_execution(success=success, latency_ms=latency_ms, retries=0)
        self._fingerprints[fp] = score
        self._events.append(
            {
                "mission_id": mission_id,
                "task_id": task_id,
                "execution_id": execution_id,
                "capability": capability,
                "tool": tool,
                "success": success,
                "latency_ms": latency_ms,
                "reason": reason,
                "fingerprint": fp,
            }
        )
        if len(self._events) > 2000:
            self._events = self._events[-2000:]
        self._metrics["outcomes_recorded"] += 1

        graph = getattr(self._app, "cognitive_memory", None)
        if graph and execution_id:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                loop.create_task(
                    graph.link_execution(
                        mission_id=mission_id,
                        task_id=task_id,
                        execution_id=execution_id,
                        summary=f"{capability} {tool or ''} {reason}"[:200],
                        success=success,
                        capability=capability,
                        tool=tool,
                    )
                )
            except RuntimeError:
                pass

    async def record_outcome_async(self, **kwargs: Any) -> None:
        self.record_outcome(**kwargs)
        graph = getattr(self._app, "cognitive_memory", None)
        if graph and kwargs.get("execution_id"):
            await graph.link_execution(
                mission_id=kwargs["mission_id"],
                task_id=kwargs.get("task_id"),
                execution_id=kwargs["execution_id"],
                summary=f"{kwargs.get('capability')} {kwargs.get('tool') or ''}"[:200],
                success=kwargs.get("success", False),
                capability=kwargs.get("capability"),
                tool=kwargs.get("tool"),
            )

    async def on_mission_completed(self, mission: Mission) -> dict[str, Any]:
        mission_events = [e for e in self._events if e.get("mission_id") == mission.mission_id]
        analysis = analyze_outcomes(mission_events)
        analysis["bottlenecks"] = [
            c["key"] for c in mine_failure_clusters(mission_events) if c.get("count", 0) >= 2
        ]
        tool_chains = mine_tool_chains(mission_events)
        failures = mine_failure_clusters(mission_events)
        successes = [e for e in mission_events if e.get("success")]

        strategy_kind = (mission.metadata.get("semantic_plan") or {}).get("strategy", {}).get(
            "kind", mission.execution_strategy
        )
        success = mission.current_state.value == "completed"
        self._strategy_stats = update_strategy_stats(
            self._strategy_stats,
            strategy_kind=str(strategy_kind),
            success=success,
            latency_ms=analysis.get("avg_latency_ms"),
        )

        retrospective = build_retrospective(
            mission,
            outcome_analysis=analysis,
            success_patterns=[{"capability": e.get("capability"), "tool": e.get("tool")} for e in successes],
            failure_clusters=failures,
            tool_chains=tool_chains,
        )
        mission.metadata["retrospective"] = retrospective
        self._metrics["retrospectives"] += 1
        self._metrics["patterns_mined"] += len(tool_chains) + len(failures)

        graph = getattr(self._app, "cognitive_memory", None)
        if graph:
            domain = (mission.metadata.get("semantic_plan") or {}).get("parsed", {}).get("domain", "general")
            await graph.upsert_entity(
                semantic_from_pattern(
                    label=f"mission:{mission.objective[:120]}",
                    domain=domain,
                    confidence=0.8 if success else 0.4,
                    metadata={"retrospective": True},
                )
            )
            stats = self._strategy_stats.get(str(strategy_kind), {})
            if stats.get("attempts", 0) >= 1:
                rate = stats.get("successes", 0) / stats["attempts"]
                await graph.upsert_entity(
                    procedural_from_strategy(
                        strategy_kind=str(strategy_kind),
                        objective_domain=domain,
                        success_rate=rate,
                        metadata=stats,
                    )
                )

        self._emit_trace(mission.mission_id, "optimization_cycle_completed", retrospective)
        return retrospective

    def strategy_stats(self) -> dict[str, dict[str, float]]:
        out: dict[str, dict[str, float]] = {}
        for k, v in self._strategy_stats.items():
            attempts = v.get("attempts", 0) or 1
            out[k] = {
                **v,
                "success_rate": v.get("successes", 0) / attempts,
                "avg_latency_ms": v.get("total_latency_ms", 0) / attempts,
            }
        return out

    def _emit_trace(self, mission_id: str, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.context import CausalTraceContext
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(
            kind,
            message=kind_name,
            payload=payload,
            component="experience_engine",
            ctx=CausalTraceContext(mission_id=mission_id),
        )
