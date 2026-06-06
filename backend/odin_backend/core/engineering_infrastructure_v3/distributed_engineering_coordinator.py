from __future__ import annotations
from typing import Any


async def distribute(app: Any, *, repos: list[str]) -> dict:
    if hasattr(app, "engineering_evolution_v2"):
        return await app.engineering_evolution_v2.analyze_multi_repo(repos=repos)
    return {"repos": repos, "distributed": True}
