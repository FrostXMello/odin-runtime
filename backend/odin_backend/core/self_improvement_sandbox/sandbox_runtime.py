"""Self-improvement sandbox (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.self_improvement_sandbox.architecture_sandbox import simulate_architecture
from odin_backend.core.self_improvement_sandbox.branch_lab import create_branch
from odin_backend.core.self_improvement_sandbox.isolated_validation import validate
from odin_backend.core.self_improvement_sandbox.performance_diffing import diff_perf
from odin_backend.core.self_improvement_sandbox.proposal_execution import execute_proposal
from odin_backend.core.self_improvement_sandbox.rollback_training import rehearse_rollback


class SelfImprovementSandboxRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._timeline: list[dict] = []

    async def experiment(self, *, name: str, proposal: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_improvement_sandbox_enabled", False):
            return {"accepted": False, "reason": "self_improvement_sandbox_disabled"}
        branch = create_branch(name)
        sim = simulate_architecture(proposal or {"name": name})
        validation = validate(branch=branch["branch"])
        self._emit("sandbox_validation_completed", validation)
        self._timeline.append({"branch": branch, "validation": validation})
        return {"accepted": True, "branch": branch, "simulation": sim, "validation": validation, "isolated": True}

    async def rollback_rehearsal(self, *, target: str = "last_stable") -> dict[str, Any]:
        r = rehearse_rollback(target=target)
        return {"accepted": True, **r}

    async def benchmark_diff(self) -> dict[str, Any]:
        before = {}
        after = {}
        if hasattr(self._app, "runtime_benchmarks"):
            before = self._app.runtime_benchmarks.snapshot()
        diff = diff_perf(before, after)
        return {"accepted": True, "diff": diff}

    def snapshot(self) -> dict[str, Any]:
        return {"experiments": len(self._timeline)}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="self_improvement_sandbox")
