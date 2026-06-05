"""Resolve stuck executions."""

from __future__ import annotations

from typing import Any


async def resolve_stuck(app: Any, *, max_age_s: float = 600) -> list[dict[str, Any]]:
    resolved: list[dict[str, Any]] = []
    runtime = getattr(app, "async_mission_runtime", None)
    if runtime and hasattr(runtime, "sweep_timeouts"):
        swept = await runtime.sweep_timeouts(max_age_s=max_age_s)
        resolved.extend(swept if isinstance(swept, list) else [])
    return resolved
