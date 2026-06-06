from __future__ import annotations


def watch(repo: str) -> dict:
    return {"repo": repo, "watching": True, "local_only": True}
