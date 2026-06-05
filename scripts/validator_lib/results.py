"""Validation result models."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ValidationStatus(StrEnum):
    PASS = "PASS"
    WARNING = "WARNING"
    FAIL = "FAIL"


@dataclass
class CheckResult:
    name: str
    status: ValidationStatus
    message: str = ""
    detail: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "detail": self.detail,
        }


@dataclass
class PhaseResult:
    phase: str
    status: ValidationStatus = ValidationStatus.PASS
    checks: list[CheckResult] = field(default_factory=list)
    duration_seconds: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, check: CheckResult) -> None:
        self.checks.append(check)
        if check.status == ValidationStatus.FAIL:
            self.status = ValidationStatus.FAIL
        elif check.status == ValidationStatus.WARNING and self.status != ValidationStatus.FAIL:
            self.status = ValidationStatus.WARNING

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "status": self.status.value,
            "duration_seconds": round(self.duration_seconds, 3),
            "checks": [c.to_dict() for c in self.checks],
            "metadata": self.metadata,
        }
