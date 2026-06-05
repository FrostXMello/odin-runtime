"""Crash recovery orchestration."""

from __future__ import annotations

from typing import Any


async def recover_from_crash(app: Any) -> dict[str, Any]:
    recovered: dict[str, Any] = {"missions": 0, "tasks": 0, "daemon": False}
    if hasattr(app, "continuity_runtime"):
        snap = await app.continuity_runtime.snapshot()
        if snap.get("active_sessions", 0) > 0:
            recovered["continuity"] = True
    if hasattr(app, "agent_execution"):
        resumed = await app.agent_execution.resume_pending()
        recovered["tasks"] = len(resumed)
    if hasattr(app, "daemon_runtime"):
        result = await app.daemon_runtime.restore_session()
        recovered["daemon"] = result.get("restored", False)
    return recovered
