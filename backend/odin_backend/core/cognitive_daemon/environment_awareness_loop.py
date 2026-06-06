from __future__ import annotations
from typing import Any


async def observe(app: Any) -> dict[str, Any]:
    if hasattr(app, "live_environment"):
        return await app.live_environment.update(duration_s=30, reason="daemon_loop")
    return {"observed": False}
