"""Failure escalation recommendations."""

from __future__ import annotations

from typing import Any

from odin_backend.core.cognition.failures.failure_classifier import FailureClass


def recommend_escalation(failure_class: FailureClass, *, oscillation: bool = False) -> dict[str, Any]:
    fixes = {
        FailureClass.TIMEOUT: ["increase timeout", "reduce batch size"],
        FailureClass.CAPABILITY: ["switch capability", "validate tool availability"],
        FailureClass.VALIDATION: ["add validation checkpoint", "inspect expected output"],
        FailureClass.OSCILLATION: ["force replan", "isolate branch", "human review"],
        FailureClass.WORKER: ["drain worker", "reroute to healthy node"],
        FailureClass.TRANSIENT: ["retry with backoff"],
        FailureClass.UNKNOWN: ["collect traces", "enable elevated observability"],
    }
    actions = list(fixes.get(failure_class, fixes[FailureClass.UNKNOWN]))
    if oscillation:
        actions.insert(0, "break retry-replan loop")
    return {"failure_class": failure_class.value, "probable_fixes": actions, "escalate": failure_class in (
        FailureClass.OSCILLATION,
        FailureClass.WORKER,
    )}
