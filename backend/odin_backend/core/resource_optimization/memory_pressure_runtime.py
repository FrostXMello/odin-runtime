"""RAM pressure monitoring."""

from __future__ import annotations

from typing import Any


def pressure_level(*, used_mb: int, total_mb: int) -> dict[str, Any]:
    ratio = used_mb / max(total_mb, 1)
    level = "critical" if ratio > 0.9 else "high" if ratio > 0.75 else "normal"
    return {"level": level, "ratio": round(ratio, 4), "used_mb": used_mb, "total_mb": total_mb}
