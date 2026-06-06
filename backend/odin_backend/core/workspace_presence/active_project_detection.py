from __future__ import annotations

def detect(*, repo: str, branch: str) -> dict:
    return {"repo": repo, "branch": branch, "active": True}
