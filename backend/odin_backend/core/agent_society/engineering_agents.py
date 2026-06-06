"""Specialized engineering agents (Prompt 39)."""

from __future__ import annotations

from typing import Any


class EngineeringAgent:
    domain: str = "general"

    def can_handle(self, task: str) -> float:
        return 0.5

    def plan(self, task: str) -> dict[str, Any]:
        return {"agent": self.domain, "task": task, "supervised": True, "approval_required": True}


class BackendArchitectAgent(EngineeringAgent):
    domain = "backend_architect"

    def can_handle(self, task: str) -> float:
        return 0.85 if any(k in task.lower() for k in ("api", "service", "architecture")) else 0.3


class DebuggerAgent(EngineeringAgent):
    domain = "debugger"

    def can_handle(self, task: str) -> float:
        return 0.9 if any(k in task.lower() for k in ("debug", "error", "stack", "fix")) else 0.2


class RefactorAgent(EngineeringAgent):
    domain = "refactor"

    def can_handle(self, task: str) -> float:
        return 0.8 if "refactor" in task.lower() else 0.25


class ResearchEngineerAgent(EngineeringAgent):
    domain = "research_engineer"

    def can_handle(self, task: str) -> float:
        return 0.75 if "research" in task.lower() else 0.3


class TestingAgent(EngineeringAgent):
    domain = "testing"

    def can_handle(self, task: str) -> float:
        return 0.85 if "test" in task.lower() else 0.2


class DocumentationAgent(EngineeringAgent):
    domain = "documentation"

    def can_handle(self, task: str) -> float:
        return 0.8 if "doc" in task.lower() else 0.2


class DevOpsAdvisorAgent(EngineeringAgent):
    domain = "devops"

    def can_handle(self, task: str) -> float:
        return 0.8 if any(k in task.lower() for k in ("deploy", "ci", "docker")) else 0.25


AGENTS: list[EngineeringAgent] = [
    BackendArchitectAgent(),
    DebuggerAgent(),
    RefactorAgent(),
    ResearchEngineerAgent(),
    TestingAgent(),
    DocumentationAgent(),
    DevOpsAdvisorAgent(),
]


def route_engineering_task(task: str) -> dict[str, Any]:
    scored = sorted(((a, a.can_handle(task)) for a in AGENTS), key=lambda x: x[1], reverse=True)
    best, score = scored[0]
    return {"agent": best.domain, "score": score, "plan": best.plan(task)}
