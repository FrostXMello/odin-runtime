"""Development workflow orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.dev_workflows.engineering_objectives import create_objective
from odin_backend.core.dev_workflows.engineering_retrospectives import generate_retrospective
from odin_backend.core.dev_workflows.implementation_planner import plan_implementation
from odin_backend.core.dev_workflows.issue_tracker import IssueTracker
from odin_backend.core.dev_workflows.milestone_tracker import MilestoneTracker
from odin_backend.core.dev_workflows.sprint_memory import SprintMemory
from odin_backend.core.dev_workflows.task_breakdown_engine import breakdown_goal


class DevWorkflowsRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._issues = IssueTracker()
        self._milestones = MilestoneTracker()
        self._sprints = SprintMemory()

    async def create_goal(self, *, title: str, repo: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "dev_workflows_enabled", False):
            return {"accepted": False, "reason": "dev_workflows_disabled"}
        objective = create_objective(title=title, repo=repo)
        tasks = breakdown_goal(goal=title)
        plan = plan_implementation(tasks=tasks)
        self._emit("engineering_goal_created", {"title": title, "tasks": len(tasks)})
        return {"accepted": True, "objective": objective, "tasks": tasks, "plan": plan}

    async def track_issue(self, *, title: str, blocked: bool = False) -> dict[str, Any]:
        issue = self._issues.add(title=title, blocked=blocked)
        if blocked:
            self._emit("implementation_blocked", {"title": title})
        return {"accepted": True, "issue": issue}

    async def retrospective(self, *, sprint: str) -> dict[str, Any]:
        retro = generate_retrospective(sprint=sprint, completed=self._issues.completed())
        return {"accepted": True, **retro}

    def snapshot(self) -> dict[str, Any]:
        return {"issues": self._issues.count(), "milestones": self._milestones.count(), "sprints": self._sprints.count()}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="dev_workflows")
