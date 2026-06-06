from __future__ import annotations

from typing import Any


def schedule_realtime(*, latency_ms: int) -> dict[str, Any]:
    return {"latency_ms": latency_ms, "priority": "high" if latency_ms < 100 else "normal"}
