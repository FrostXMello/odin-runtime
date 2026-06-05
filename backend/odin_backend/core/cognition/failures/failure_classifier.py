"""Failure classification."""

from __future__ import annotations

from enum import StrEnum


class FailureClass(StrEnum):
    TRANSIENT = "transient"
    CAPABILITY = "capability"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    OSCILLATION = "oscillation"
    WORKER = "worker"
    UNKNOWN = "unknown"


def classify_failure(*, reason: str, execution_state: str, retry_count: int) -> FailureClass:
    lower = (reason + execution_state).lower()
    if "timeout" in lower or execution_state == "timed_out":
        return FailureClass.TIMEOUT
    if "validation" in lower:
        return FailureClass.VALIDATION
    if retry_count >= 3:
        return FailureClass.OSCILLATION
    if "worker" in lower or "stale" in lower:
        return FailureClass.WORKER
    if "capability" in lower or "executor" in lower:
        return FailureClass.CAPABILITY
    if "retry" in lower or "transient" in lower:
        return FailureClass.TRANSIENT
    return FailureClass.UNKNOWN
