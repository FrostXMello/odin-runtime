"""Runtime evolution orchestrator — behavioral adaptation only."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from odin_backend.core.runtime_evolution.adaptive_throttling import throttle_factor
from odin_backend.core.runtime_evolution.execution_economy import ExecutionEconomy
from odin_backend.core.runtime_evolution.latency_optimizer import recommend
from odin_backend.core.runtime_evolution.mission_cost_analysis import analyze_mission_cost
from odin_backend.core.runtime_evolution.policy_optimizer import optimize_policy
from odin_backend.core.runtime_evolution.reasoning_efficiency import efficiency
from odin_backend.core.runtime_evolution.routing_optimizer import optimize_routing


class EvolutionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._economy = ExecutionEconomy()
        self._weights = {"routing": 0.5, "planning": 0.5, "retry": 0.3}
        self._cycles: list[dict[str, Any]] = []

    async def optimize(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "runtime_evolution_enabled", False):
            return {"accepted": False, "reason": "runtime_evolution_disabled"}
        policy = optimize_policy(self._weights, success_rate=0.7)
        self._weights = policy["weights"]
        self._emit("policy_optimized", policy)
        routing = optimize_routing(latency_ms=50.0, success=0.8)
        self._emit("routing_optimized", routing)
        throttle = throttle_factor(load=0.4)
        eff = efficiency(tokens=500, success=True, latency_ms=120)
        lat = recommend(p50=50, p99=200)
        cycle = {
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "policy": policy,
            "routing": routing,
            "throttle": throttle,
            "efficiency": eff,
            "latency": lat,
        }
        self._cycles.append(cycle)
        self._emit("evolution_cycle_completed", {"cycle_count": len(self._cycles)})
        return {"accepted": True, "cycle": cycle}

    def record_execution_cost(self, cost: float) -> None:
        self._economy.record(cost)

    def mission_economy(self, mission_id: str) -> dict[str, Any]:
        return analyze_mission_cost(mission_id=mission_id, tokens=1000, duration_s=30.0)

    def snapshot(self) -> dict[str, Any]:
        return {
            "weights": dict(self._weights),
            "economy": self._economy.snapshot(),
            "cycles": len(self._cycles),
            "last_cycle": self._cycles[-1] if self._cycles else None,
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="runtime_evolution")
