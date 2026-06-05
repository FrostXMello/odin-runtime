"""Simple anomaly detection for runtime metrics."""

from __future__ import annotations

from typing import Any


def detect_anomalies(metrics: dict[str, Any], *, thresholds: dict[str, float] | None = None) -> list[dict[str, Any]]:
    th = thresholds or {"failure_rate": 0.5, "retry_rate": 0.4, "plan_confidence": 0.35}
    anomalies: list[dict[str, Any]] = []
    if metrics.get("failure_rate", 0) > th["failure_rate"]:
        anomalies.append({"kind": "high_failure_rate", "value": metrics["failure_rate"]})
    if metrics.get("retry_rate", 0) > th["retry_rate"]:
        anomalies.append({"kind": "high_retry_rate", "value": metrics["retry_rate"]})
    if metrics.get("plan_confidence", 1) < th["plan_confidence"]:
        anomalies.append({"kind": "low_plan_confidence", "value": metrics["plan_confidence"]})
    return anomalies
