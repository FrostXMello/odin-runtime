from __future__ import annotations


class DecisionMemory:
    def __init__(self) -> None:
        self._decisions: list[dict] = []

    def record(self, decision: str, rationale: str) -> dict:
        item = {"decision": decision[:80], "rationale": rationale[:160]}
        self._decisions.append(item)
        return item
