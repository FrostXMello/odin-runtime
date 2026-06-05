"""Window management stubs."""

from __future__ import annotations

from typing import Any


async def focus_window(app: Any, *, title: str) -> dict[str, Any]:
    return {"simulated": getattr(app.settings, "automation_simulation_mode", True), "title": title}
