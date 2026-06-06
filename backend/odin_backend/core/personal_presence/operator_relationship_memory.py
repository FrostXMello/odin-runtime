from __future__ import annotations


class RelationshipMemory:
    def __init__(self) -> None:
        self._interactions = 0

    def interact(self) -> dict:
        self._interactions += 1
        return {"interactions": self._interactions}
