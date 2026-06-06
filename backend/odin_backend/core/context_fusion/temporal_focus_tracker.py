from __future__ import annotations

from typing import Any


def track_focus(*, active_app: str) -> dict[str, Any]:
    intensity = 0.8 if active_app not in ("unknown", "idle") else 0.2
    return {"app": active_app, "intensity": intensity}
