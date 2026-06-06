from __future__ import annotations
from typing import Any

def observe(*, repo: str, branch: str = "main", dirty: bool = False) -> dict[str, Any]:
    return {"repo": repo, "branch": branch, "dirty": dirty, "engineering_active": True}
