"""Self-healing execution orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.self_healing.dependency_healer import heal_dependencies
from odin_backend.core.self_healing.execution_forensics import analyze_lineage
from odin_backend.core.self_healing.mission_salvage import salvage_mission
from odin_backend.core.self_healing.recovery_planner import plan_recovery
from odin_backend.core.self_healing.retry_optimizer import optimize_retry
from odin_backend.core.self_healing.stuck_execution_resolver import resolve_stuck


class SelfHealingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._salvages = 0
        self._repairs = 0

    async def heal(self, *, mission_id: str | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_healing_enabled", False):
            return {"accepted": False, "reason": "self_healing_disabled"}
        actions: list[str] = []
        stuck = await resolve_stuck(self._app)
        if stuck:
            actions.append("stuck_resolved")
            self._repairs += 1
        healed_deps: list[str] = []
        if hasattr(self._app, "kernel"):
            healed_deps = heal_dependencies(self._app.kernel.task_graph)
            if healed_deps:
                actions.append("dependencies_healed")
        salvaged = None
        if mission_id:
            salvaged = await salvage_mission(self._app, mission_id)
            if salvaged.get("salvaged"):
                self._salvages += 1
                self._emit("execution_salvaged", salvaged)
                actions.append("mission_salvaged")
        plan = plan_recovery(mission_state="running", failed_tasks=len(stuck), blocked_tasks=len(healed_deps))
        retry = optimize_retry(attempt=self._repairs, failure_rate=0.3)
        return {
            "accepted": True,
            "actions": actions,
            "stuck": stuck,
            "healed_dependencies": healed_deps,
            "salvaged": salvaged,
            "plan": plan,
            "retry": retry,
        }

    def forensics(self, executions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        data = executions or []
        return analyze_lineage(data)

    def snapshot(self) -> dict[str, Any]:
        return {"salvages": self._salvages, "repairs": self._repairs}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_healing")
