"""Colored console output for validators."""

import sys

from validator_lib.results import CheckResult, PhaseResult, ValidationStatus


class ColoredConsole:
    """ANSI-colored terminal output (Windows 10+ compatible)."""

    def __init__(self, *, enabled: bool = True) -> None:
        self._enabled = enabled and sys.stdout.isatty()

    def _c(self, text: str, code: str) -> str:
        if not self._enabled:
            return text
        return f"\033[{code}m{text}\033[0m"

    def header(self, text: str) -> None:
        print(self._c(f"\n{'=' * 60}\n{text}\n{'=' * 60}", "1;36"))

    def info(self, text: str) -> None:
        print(self._c(f"  [i] {text}", "36"))

    def pass_(self, text: str) -> None:
        print(self._c(f"  [PASS] {text}", "32"))

    def warn(self, text: str) -> None:
        print(self._c(f"  [WARN] {text}", "33"))

    def fail(self, text: str) -> None:
        print(self._c(f"  [FAIL] {text}", "31"))

    def status_line(self, status: ValidationStatus, label: str) -> None:
        if status == ValidationStatus.PASS:
            self.pass_(label)
        elif status == ValidationStatus.WARNING:
            self.warn(label)
        else:
            self.fail(label)

    def print_check(self, check: CheckResult) -> None:
        prefix = f"{check.name}: {check.message}" if check.message else check.name
        self.status_line(check.status, prefix)

    def print_phase(self, phase: PhaseResult) -> None:
        self.header(f"Phase: {phase.phase} — {phase.status.value}")
        for check in phase.checks:
            self.print_check(check)
        if phase.metadata:
            self.info(f"metadata: {phase.metadata}")
