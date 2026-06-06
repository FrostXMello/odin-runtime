from __future__ import annotations

ROLES = (
    "Architect", "Backend Engineer", "Frontend Engineer", "Debugger",
    "QA Engineer", "DevOps Engineer", "Reviewer", "Research Engineer",
)


def assign(task: str) -> list[str]:
    if "debug" in task.lower():
        return ["Debugger", "QA Engineer"]
    if "arch" in task.lower():
        return ["Architect", "Reviewer"]
    return ["Backend Engineer", "Reviewer"]
