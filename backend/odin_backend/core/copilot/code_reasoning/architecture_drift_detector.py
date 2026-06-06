from __future__ import annotations

from typing import Any


def detect_drift(*, current: dict[str, Any], prior: dict[str, Any] | None) -> dict[str, Any]:
    if not prior:
        return {"drift_detected": False, "reason": "no_baseline"}
    delta = abs(current.get("nodes", 0) - len(prior.get("files", [])))
    return {"drift_detected": delta > 5, "delta_nodes": delta}
