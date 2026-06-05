"""Interruptible speech detection."""

from __future__ import annotations

from typing import Any


class InterruptionDetection:
    def __init__(self) -> None:
        self._interrupted = False

    def signal(self) -> None:
        self._interrupted = True

    def check(self) -> dict[str, Any]:
        result = {"interrupted": self._interrupted}
        self._interrupted = False
        return result
