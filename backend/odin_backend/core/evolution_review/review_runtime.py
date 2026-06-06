"""Supervised evolution review workflow (Prompt 46)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.evolution_review.approval_workflows import review_action
from odin_backend.core.evolution_review.benchmark_diffs import diff_benchmarks
from odin_backend.core.evolution_review.patch_timeline import PatchTimeline
from odin_backend.core.evolution_review.proposal_queue import ProposalQueue
from odin_backend.core.evolution_review.regression_compare import compare
from odin_backend.core.evolution_review.rollback_explorer import simulate_rollback
from odin_backend.core.evolution_review.upgrade_visualizer import visualize_upgrade


class EvolutionReviewRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._queue = ProposalQueue()
        self._timeline = PatchTimeline()

    async def open_review(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "evolution_review_enabled", False):
            return {"accepted": False, "reason": "evolution_review_disabled"}
        review = {}
        if hasattr(self._app, "self_evolution"):
            review["evolution"] = self._app.self_evolution.snapshot()
        if hasattr(self._app, "runtime_benchmarks"):
            review["benchmarks"] = self._app.runtime_benchmarks.snapshot()
        if hasattr(self._app, "autonomous_patching"):
            review["patching"] = self._app.autonomous_patching.snapshot()
        viz = visualize_upgrade(review)
        self._queue.enqueue({"kind": "upgrade", "review": review})
        self._emit("upgrade_review_opened", {"sections": list(review.keys())})
        return {"accepted": True, "review": review, "visual": viz, "approval_required": True}

    async def compare_benchmarks(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "evolution_review_enabled", False):
            return {"accepted": False, "reason": "evolution_review_disabled"}
        current = {}
        baseline = {}
        if hasattr(self._app, "runtime_benchmarks"):
            current = self._app.runtime_benchmarks.snapshot()
        diff = diff_benchmarks(current, baseline)
        return {"accepted": True, "diff": diff}

    async def simulate_rollback(self, *, target: str = "last_stable") -> dict[str, Any]:
        sim = simulate_rollback(target=target)
        self._emit("rollback_simulated", sim)
        self._timeline.add({"kind": "rollback_sim", **sim})
        return {"accepted": True, **sim}

    async def decide(self, *, action: str, proposal_id: str = "latest") -> dict[str, Any]:
        result = review_action(action=action, proposal_id=proposal_id)
        return result

    def snapshot(self) -> dict[str, Any]:
        return {"pending": len(self._queue.pending()), "timeline": self._timeline.history()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="evolution_review")
