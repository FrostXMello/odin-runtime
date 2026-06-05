"""Emergency recovery procedures."""

from __future__ import annotations

from typing import Any

from odin_backend.core.stability.crash_recovery import recover_from_crash
from odin_backend.core.stability.degraded_operation import activate_degraded
from odin_backend.core.stability.runtime_repair import repair_runtime


async def emergency_recover(app: Any) -> dict[str, Any]:
    degraded = activate_degraded(reason="emergency_recovery", level="emergency")
    if hasattr(app, "resource_optimization"):
        app.resource_optimization.set_mode("minimal")
    repair = await repair_runtime(app, reason="emergency")
    crash = await recover_from_crash(app)
    return {"degraded": degraded, "repair": repair, "crash_recovery": crash}
