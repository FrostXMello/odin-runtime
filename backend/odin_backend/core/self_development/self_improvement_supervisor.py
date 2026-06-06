"""Supervised self-development — proposals only, no direct modification."""
from __future__ import annotations
from typing import Any

from odin_backend.core.self_development.architecture_reflection import reflect
from odin_backend.core.self_development.capability_gap_detector import detect_gaps
from odin_backend.core.self_development.improvement_queue import ImprovementQueue
from odin_backend.core.self_development.learning_opportunity_engine import opportunities
from odin_backend.core.self_development.patch_proposal_pipeline import propose_patch
from odin_backend.core.self_development.supervised_evolution import evolve


class SelfDevelopmentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue = ImprovementQueue()

    async def analyze(self, *, metrics: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_development_enabled", False):
            return {"accepted": False, "reason": "self_development_disabled"}
        m = metrics or {"latency_ms": 320, "error_rate": 0.01}
        gaps = detect_gaps(metrics=m)
        ops = opportunities(gaps=gaps)
        reflection = reflect(components=["cognitive_shell", "conversation_runtime", "presence"])
        for op in ops:
            item = self._queue.enqueue(op)
            self._emit("improvement_proposed", item)
        self._emit("architecture_reflection_generated", reflection)
        return {
            "accepted": True,
            "gaps": gaps,
            "opportunities": ops,
            "reflection": reflection,
            "approval_required": True,
            "direct_modification": False,
        }

    async def propose(self, *, title: str, plan: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_development_enabled", False):
            return {"accepted": False, "reason": "self_development_disabled"}
        proposal = propose_patch(title=title, plan=plan or ["analyze", "draft patch", "await approval"])
        item = self._queue.enqueue(proposal)
        evo = evolve(proposal=proposal)
        self._emit("improvement_proposed", item)
        return {"accepted": True, "proposal": proposal, "evolution": evo, "approval_required": True}

    def snapshot(self) -> dict[str, Any]:
        return {"queue": self._queue.snapshot(), "direct_modification": False}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_development")
