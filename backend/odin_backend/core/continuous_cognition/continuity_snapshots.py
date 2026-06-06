from __future__ import annotations

from typing import Any


def snapshot_state(*, ticks: int, deferred: int) -> dict[str, Any]:
    return {"ticks": ticks, "deferred": deferred, "continuity": True}
