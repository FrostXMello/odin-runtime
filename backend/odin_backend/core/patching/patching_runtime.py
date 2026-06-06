"""Safe supervised patching orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.patching.branch_isolation import isolate_branch
from odin_backend.core.patching.diff_validator import validate_diff
from odin_backend.core.patching.patch_planner import plan_patch
from odin_backend.core.patching.patch_risk_engine import assess_risk
from odin_backend.core.patching.patch_sandbox import sandbox_patch
from odin_backend.core.patching.rollback_generator import generate_rollback
from odin_backend.core.patching.test_impact_analysis import analyze_test_impact


class PatchingRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._patches: list[dict] = []

    async def plan(self, *, goal: str, files: list[str]) -> dict[str, Any]:
        if not getattr(self._app.settings, "safe_patching_enabled", False):
            return {"accepted": False, "reason": "safe_patching_disabled"}
        plan = plan_patch(goal=goal, files=files)
        risk = assess_risk(files=files, touches_main=False)
        branch = isolate_branch(prefix="odin-patch")
        rollback = generate_rollback(plan_id=plan["plan_id"])
        self._emit("rollback_prepared", rollback)
        self._emit("patch_generated", {"goal": goal[:80], "files": len(files)})
        return {
            "accepted": True,
            "plan": plan,
            "risk": risk,
            "branch": branch,
            "rollback": rollback,
            "requires_approval": True,
            "no_main_commit": True,
        }

    async def sandbox_apply(self, *, diff: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "safe_patching_enabled", False):
            return {"accepted": False, "reason": "safe_patching_disabled"}
        valid = validate_diff(diff=diff)
        if not valid["valid"]:
            return {"accepted": False, "reason": "invalid_diff", "validation": valid}
        sandboxed = sandbox_patch(diff=diff)
        impact = analyze_test_impact(diff=diff)
        self._emit("patch_validated", {"sandbox": True, "impact": impact["impacted"]})
        self._patches.append({"diff_len": len(diff), "sandbox": True})
        return {"accepted": True, "sandbox": sandboxed, "impact": impact, "requires_approval": True}

    def snapshot(self) -> dict[str, Any]:
        return {"patches": len(self._patches)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="patching")
