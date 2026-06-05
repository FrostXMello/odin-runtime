"""Schedule awareness."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def schedule_context(*, hour: int | None = None) -> dict[str, Any]:
    hour = hour if hour is not None else datetime.now(timezone.utc).hour
    if hour < 12:
        period = "morning"
    elif hour < 17:
        period = "afternoon"
    else:
        period = "evening"
    return {"hour": hour, "period": period}
