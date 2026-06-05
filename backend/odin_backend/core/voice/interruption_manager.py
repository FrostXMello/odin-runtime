"""Low-latency voice interruption handling."""

from __future__ import annotations


class InterruptionManager:
    def __init__(self) -> None:
        self._interrupted = False

    def interrupt(self) -> None:
        self._interrupted = True

    def clear(self) -> None:
        self._interrupted = False

    @property
    def interrupted(self) -> bool:
        return self._interrupted
