from __future__ import annotations
from typing import Any


async def coordinate(app: Any, *, repo: str) -> dict:
    if hasattr(app, "engineering_evolution_v2"):
        return await app.engineering_evolution_v2.analyze_multi_repo(repos=[repo])
    return {"repo": repo, "coordinated": True}
