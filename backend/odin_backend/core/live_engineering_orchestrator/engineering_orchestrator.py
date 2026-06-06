"""Live engineering orchestrator (Prompt 47)."""
from __future__ import annotations
from typing import Any
from uuid import uuid4

from odin_backend.core.live_engineering_orchestrator.active_issue_tracker import ActiveIssueTracker
from odin_backend.core.live_engineering_orchestrator.code_focus import infer_goal
from odin_backend.core.live_engineering_orchestrator.debug_watchtower import watch
from odin_backend.core.live_engineering_orchestrator.repo_attention import drift_score
from odin_backend.core.live_engineering_orchestrator.session_coordinator import load_session, save_session
from odin_backend.core.live_engineering_orchestrator.task_supervisor import supervise
from odin_backend.core.live_engineering_orchestrator.work_context import build_context

PROFILES = ("lightweight_engineering", "balanced_engineering", "autonomous_engineering", "overnight_engineering")


class LiveEngineeringOrchestratorRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._session_id = str(uuid4())
        self._issues = ActiveIssueTracker()
        self._profile = "balanced_engineering"
        self._path = "./data/engineering_session.json"

    async def observe(self, *, repo: str, file: str = "", error: str = "", logs: list[str] | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_engineering_orchestrator_enabled", False):
            return {"accepted": False, "reason": "live_engineering_orchestrator_disabled"}
        goal = infer_goal(file=file or repo, error=error)
        ctx = build_context(repo=repo, goal=goal, files=[file] if file else [])
        tower = watch(logs=logs or [], errors=[error] if error else [])
        drift = drift_score(dirty_files=1 if error else 0, stale_hours=0.5)
        live = {}
        if hasattr(self._app, "live_engineering"):
            live = await self._app.live_engineering.session(repo=repo, ide={"file": file}, error=error)
        self._emit("engineering_goal_detected", {"goal": goal, "repo": repo})
        caps = {"lightweight_engineering": 15, "balanced_engineering": 30, "autonomous_engineering": 45, "overnight_engineering": 10}
        return {
            "accepted": True,
            "session_id": self._session_id,
            "context": ctx,
            "watchtower": tower,
            "drift": drift,
            "live_engineering": live,
            "open_issues": self._issues.open_issues(),
            "supervised": True,
            "fps_cap": caps.get(self._profile, 30),
        }

    async def restore(self) -> dict[str, Any]:
        restored = load_session(path=self._path)
        if restored.get("restored"):
            self._emit("engineering_session_restored", restored.get("data", {}))
        return {"accepted": True, **restored}

    async def checkpoint(self, *, state: dict | None = None) -> dict[str, Any]:
        payload = state or {"session_id": self._session_id, "issues": self._issues.open_issues()}
        save_session(path=self._path, data=payload)
        return {"accepted": True, "checkpoint": payload}

    async def set_profile(self, profile: str) -> dict[str, Any]:
        if profile not in PROFILES:
            return {"accepted": False, "reason": "invalid_profile"}
        self._profile = profile
        return {"accepted": True, "profile": profile, "stream_batching": profile != "autonomous_engineering"}

    def snapshot(self) -> dict[str, Any]:
        return {"session_id": self._session_id, "profile": self._profile, "issues": len(self._issues.open_issues())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_engineering_orchestrator")
