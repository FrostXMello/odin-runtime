from __future__ import annotations
from typing import Any


async def analyze(app: Any, *, repo: str) -> dict:
    return {"repo": repo, "analysis": "deferred thoughts compiled", "local_only": True}
