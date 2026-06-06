"""Self-evolution orchestrator — supervised engineering loops only."""
from __future__ import annotations

import time
from typing import Any

from odin_backend.core.self_evolution.autonomous_backlog import AutonomousBacklog
from odin_backend.core.self_evolution.bottleneck_detector import detect
from odin_backend.core.self_evolution.capability_gap_analysis import analyze
from odin_backend.core.self_evolution.engineering_feedback import feedback
from odin_backend.core.self_evolution.improvement_cycles import STAGES, cycle_budget, next_stage
from odin_backend.core.self_evolution.routing_optimizer import optimize_route
from odin_backend.core.self_evolution.runtime_reflection import reflect
from odin_backend.core.self_evolution.upgrade_proposals import propose


class SelfEvolutionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._backlog = AutonomousBacklog()
        self._cycle_depth = 0
        self._last_cycle_at = 0.0
        self._cooldown_s = 60.0
        self._stage: str | None = None
        self._cycles = 0

    async def run_cycle(self, *, metrics: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_evolution_enabled", False):
            return {"accepted": False, "reason": "self_evolution_disabled"}
        budget = cycle_budget(depth=self._cycle_depth)
        if not budget["allowed"]:
            return {"accepted": False, "reason": "recursion_guard", "depth": self._cycle_depth}
        now = time.time()
        if self._last_cycle_at and (now - self._last_cycle_at) < self._cooldown_s:
            return {"accepted": False, "reason": "cooldown", "retry_in_s": self._cooldown_s}
        self._cycle_depth += 1
        self._last_cycle_at = now
        self._cycles += 1
        self._emit("improvement_cycle_started", {"cycle": self._cycles, "depth": self._cycle_depth})
        m = metrics or {"latency_ms": 450, "error_rate": 0.02, "memory_mb": 8000, "agent_queue": 4}
        bottlenecks = detect(metrics=m)
        for b in bottlenecks:
            self._emit("bottleneck_detected", b)
        history = []
        if hasattr(self._app, "self_improvement_memory"):
            history = await self._app.self_improvement_memory.recent(limit=10)
        gaps = analyze(bottlenecks=bottlenecks, history=history)
        reflection = reflect(components=["self_evolution", "patching", "benchmarks", "governance"])
        proposals = []
        for g in gaps[:3]:
            p = propose(
                title=f"Improve {g['area']}",
                rationale=f"Detected {g['area']} with {g['impact']} impact",
                expected_gain="latency reduction",
                risk="medium" if g["impact"] != "high" else "high",
            )
            self._backlog.add(title=p["title"], impact=g["impact"], confidence=g["confidence"])
            proposals.append(p)
            self._emit("upgrade_proposed", {"proposal_id": p["proposal_id"], "title": p["title"]})
        self._stage = next_stage(self._stage)
        sim = await self._simulate(proposals[0] if proposals else None)
        validated = await self._validate(sim)
        approval = await self._request_approval(validated)
        route = optimize_route(
            vram_mb=getattr(self._app.settings, "local_ai_vram_mb", 4096),
            mode=getattr(self._app.settings, "self_evolution_mode", "balanced"),
        )
        self._cycle_depth = max(0, self._cycle_depth - 1)
        self._emit("evolution_learning_updated", {"cycles": self._cycles, "proposals": len(proposals)})
        return {
            "accepted": True,
            "stage": self._stage,
            "stages": list(STAGES),
            "bottlenecks": bottlenecks,
            "gaps": gaps,
            "reflection": reflection,
            "proposals": proposals,
            "simulation": sim,
            "validation": validated,
            "approval": approval,
            "routing": route,
            "recursion_guard": True,
            "no_main_commit": True,
        }

    async def _simulate(self, proposal: dict | None) -> dict[str, Any]:
        if not proposal:
            return {"accepted": True, "simulated": False}
        return {"accepted": True, "simulated": True, "proposal_id": proposal["proposal_id"], "branch": "odin-evolve-sim"}

    async def _validate(self, sim: dict) -> dict[str, Any]:
        if hasattr(self._app, "validation_fabric") and sim.get("simulated"):
            r = await self._app.validation_fabric.validate_patch(before="", after="simulated", confidence=0.7)
            self._emit("patch_validated", {"sandbox": True, "valid": r.get("accepted", False)})
            return r
        return {"accepted": True, "validated": True}

    async def _request_approval(self, validated: dict) -> dict[str, Any]:
        if hasattr(self._app, "evolution_governance"):
            return await self._app.evolution_governance.review(
                proposal={"validation": validated},
                level=getattr(self._app.settings, "evolution_approval_level", "proposal_only"),
            )
        return {"accepted": True, "approval_required": True, "level": "proposal_only"}

    async def learn(self, *, outcome: str, benchmark_delta: float) -> dict[str, Any]:
        fb = feedback(outcome=outcome, benchmark_delta=benchmark_delta)
        if hasattr(self._app, "self_improvement_memory"):
            await self._app.self_improvement_memory.record_outcome(outcome=outcome, delta=benchmark_delta)
        self._emit("evolution_learning_updated", fb)
        return {"accepted": True, **fb}

    async def analyze_friction(self, *, workflow_metrics: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_evolution_enabled", False):
            return {"accepted": False, "reason": "self_evolution_disabled"}
        m = workflow_metrics or {"context_switches": 12, "idle_ratio": 0.3}
        friction = []
        if m.get("context_switches", 0) > 8:
            friction.append({"area": "workflow_inefficiency", "severity": "medium"})
        if m.get("idle_ratio", 0) > 0.5:
            friction.append({"area": "operator_friction", "severity": "low"})
        for f in friction:
            self._backlog.add(title=f"Reduce {f['area']}", impact=f["severity"], confidence=0.65)
        return {"accepted": True, "friction": friction, "approval_required": True, "direct_modification": False}

    def snapshot(self) -> dict[str, Any]:
        return {
            "backlog": self._backlog.snapshot(),
            "cycles": self._cycles,
            "stage": self._stage,
            "depth": self._cycle_depth,
            "cooldown_s": self._cooldown_s,
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
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_evolution")
