from __future__ import annotations

from typing import Any


def build_horizon(*, threads: list[dict]) -> dict[str, Any]:
    return {"threads": len(threads), "horizon_days": 30}
