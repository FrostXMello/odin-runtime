from __future__ import annotations


def plan_repo(repo: str) -> dict:
    return {"repo": repo, "milestones": ["scaffold", "implement", "test"]}
