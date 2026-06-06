"""Technical decision log."""

from __future__ import annotations

from typing import Any


class TechnicalDecisions:
    def __init__(self) -> None:
        self._decisions: list[dict[str, Any]] = []

    def record(self, *, repo: str, decision: str, rationale: str) -> dict[str, Any]:
        entry = {"repo": repo, "decision": decision, "rationale": rationale}
        self._decisions.append(entry)
        return entry

    def count(self) -> int:
        return len(self._decisions)
