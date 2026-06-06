from __future__ import annotations
from typing import Any


def build_context(*, repo: str, goal: str = "", files: list[str] | None = None) -> dict[str, Any]:
    return {"repo": repo, "goal": goal[:160], "files": files or [], "continuity": True}
