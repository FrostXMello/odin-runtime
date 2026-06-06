"""Autonomous patch pipeline — isolated branches, mandatory rollback."""
from __future__ import annotations
from typing import Any

from odin_backend.core.autonomous_patching.benchmark_runner import run as run_bench
from odin_backend.core.autonomous_patching.branch_manager import create_branch
from odin_backend.core.autonomous_patching.merge_recommendation import recommend
from odin_backend.core.autonomous_patching.patch_planner import plan
from odin_backend.core.autonomous_patching.patch_sandbox import sandbox
from odin_backend.core.autonomous_patching.patch_validator import validate
from odin_backend.core.autonomous_patching.rollback_engine import prepare


class AutonomousPatchingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._runs: list[dict] = []

    async def pipeline(self, *, goal: str, files: list[str], diff: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "autonomous_patching_loop_enabled", False):
            return {"accepted": False, "reason": "autonomous_patching_loop_disabled"}
        p = plan(goal=goal, files=files)
        branch = create_branch(prefix="odin-evolve")
        rollback = prepare(branch=branch["branch"])
        self._emit("patch_generated", {"plan_id": p["plan_id"], "branch": branch["branch"]})
        if diff:
            v = validate(diff=diff)
            if not v["valid"]:
                return {"accepted": False, "reason": "invalid_patch", "validation": v}
            work = str(getattr(self._app.settings, "sandbox_work_dir", "./sandbox"))
            sb = sandbox(diff=diff, work_dir=work)
            if hasattr(self._app, "patching"):
                ext = await self._app.patching.sandbox_apply(diff=diff)
                sb["external"] = ext.get("accepted", False)
            self._emit("patch_validated", {"plan_id": p["plan_id"], "sandbox": True})
        bench = run_bench()
        regression = bench["delta_pct"] < -5
        if regression:
            self._emit("regression_detected", {"delta_pct": bench["delta_pct"]})
            self._emit("rollback_triggered", rollback)
            if hasattr(self._app, "self_improvement_memory"):
                await self._app.self_improvement_memory.record_regression(metric="benchmark", delta=bench["delta_pct"])
        rec = recommend(confidence=0.75 if not regression else 0.3, regression=regression)
        self._runs.append({"plan_id": p["plan_id"], "branch": branch["branch"]})
        return {
            "accepted": True,
            "plan": p,
            "branch": branch,
            "rollback": rollback,
            "benchmark": bench,
            "regression": regression,
            "recommendation": rec,
            "no_main_commit": True,
            "approval_required": True,
        }

    async def rollback(self, *, branch: str) -> dict[str, Any]:
        rb = prepare(branch=branch)
        self._emit("rollback_triggered", rb)
        return {"accepted": True, "rollback": rb}

    def snapshot(self) -> dict[str, Any]:
        return {"runs": len(self._runs)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="autonomous_patching")
