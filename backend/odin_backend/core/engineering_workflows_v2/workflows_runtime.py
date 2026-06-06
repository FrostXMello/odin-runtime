"""Engineering workflows v2 (Prompt 47)."""
from __future__ import annotations
from typing import Any

from odin_backend.core.engineering_workflows_v2.execution_checkpoints import checkpoint
from odin_backend.core.engineering_workflows_v2.goal_pipeline import pipeline
from odin_backend.core.engineering_workflows_v2.implementation_stages import STAGES, advance
from odin_backend.core.engineering_workflows_v2.milestone_tracking import MilestoneTracker
from odin_backend.core.engineering_workflows_v2.repo_planner import plan_repo
from odin_backend.core.engineering_workflows_v2.task_breakdown import breakdown
from odin_backend.core.engineering_workflows_v2.workflow_state import load_state, save_state


class EngineeringWorkflowsV2Runtime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._stage = "plan"
        self._milestones = MilestoneTracker()
        self._path = "./data/engineering_workflow.json"

    async def plan(self, *, goal: str, repo: str = "local") -> dict[str, Any]:
        if not getattr(self._app.settings, "engineering_workflows_v2_enabled", False):
            return {"accepted": False, "reason": "engineering_workflows_v2_disabled"}
        steps = pipeline(goal)
        tasks = breakdown(goal)
        repo_plan = plan_repo(repo)
        for m in repo_plan.get("milestones", []):
            self._milestones.add(m)
        state = {"goal": goal, "stage": self._stage, "tasks": tasks}
        save_state(path=self._path, state=state)
        return {"accepted": True, "pipeline": steps, "tasks": tasks, "repo_plan": repo_plan, "supervised": True}

    async def advance_stage(self) -> dict[str, Any]:
        nxt = advance(self._stage)
        self._stage = nxt
        self._emit("implementation_stage_advanced", {"stage": nxt})
        cp = checkpoint(nxt, {"stage": nxt})
        return {"accepted": True, "stage": nxt, "checkpoint": cp}

    async def resume(self) -> dict[str, Any]:
        state = load_state(path=self._path)
        if state:
            self._stage = state.get("stage", self._stage)
        return {"accepted": True, "state": state, "milestones": self._milestones.list()}

    def snapshot(self) -> dict[str, Any]:
        return {"stage": self._stage, "milestones": self._milestones.list()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="engineering_workflows_v2")
