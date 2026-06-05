"""Token cost accounting."""

from __future__ import annotations

from typing import Any


class TokenEconomy:
    def __init__(self) -> None:
        self._ledger: list[dict[str, Any]] = []

    def charge(self, *, mission_id: str | None, tokens: int, model: str) -> dict[str, Any]:
        entry = {"mission_id": mission_id, "tokens": tokens, "model": model}
        self._ledger.append(entry)
        return entry

    def total_for_mission(self, mission_id: str) -> int:
        return sum(e["tokens"] for e in self._ledger if e.get("mission_id") == mission_id)
