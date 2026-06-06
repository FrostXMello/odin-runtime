from __future__ import annotations
from typing import Any


async def tick(app: Any, *, idle_s: float) -> dict:
    out = {"idle_s": idle_s}
    if hasattr(app, "live_engineering_orchestrator"):
        orch = app.live_engineering_orchestrator
        if getattr(app.settings, "live_engineering_orchestrator_enabled", False):
            out["orchestrator"] = await orch.observe(repo="local")
    return out
