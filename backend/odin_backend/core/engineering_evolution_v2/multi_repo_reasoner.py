from __future__ import annotations


def reason(*, repos: list[str]) -> dict:
    return {"repos": repos[:8], "links": len(repos), "local_only": True}
