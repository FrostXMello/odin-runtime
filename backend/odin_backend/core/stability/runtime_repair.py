"""Runtime repair actions."""

from __future__ import annotations

from typing import Any

from odin_backend.core.stability.orphan_cleanup import cleanup_orphans


async def repair_runtime(app: Any, *, reason: str = "watchdog") -> dict[str, Any]:
    repairs: list[str] = []
    orphans = await cleanup_orphans(app)
    if orphans["cleaned"]:
        repairs.append("orphan_cleanup")
    if hasattr(app, "async_mission_runtime") and hasattr(app.async_mission_runtime, "sweep_timeouts"):
        swept = await app.async_mission_runtime.sweep_timeouts()
        if swept:
            repairs.append("execution_timeout_sweep")
    if hasattr(app, "local_ai"):
        for model in list(getattr(app.local_ai, "_loaded", set())):
            await app.local_ai.evict(model)
            repairs.append(f"model_evicted:{model}")
    return {"repaired": repairs, "orphans": orphans, "reason": reason}
