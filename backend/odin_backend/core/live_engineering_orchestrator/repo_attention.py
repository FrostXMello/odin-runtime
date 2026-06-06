from __future__ import annotations


def drift_score(*, dirty_files: int, stale_hours: float) -> float:
    return min(1.0, dirty_files * 0.05 + stale_hours / 48.0)
