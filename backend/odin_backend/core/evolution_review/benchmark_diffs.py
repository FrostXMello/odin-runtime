from __future__ import annotations
from typing import Any


def diff_benchmarks(current: dict, baseline: dict) -> dict[str, Any]:
    return {"current": current, "baseline": baseline, "drift_detected": current != baseline}
