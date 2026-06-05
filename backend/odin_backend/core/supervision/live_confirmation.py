"""Live step confirmations."""

from __future__ import annotations

from typing import Any


class LiveConfirmation:
    def __init__(self) -> None:
        self._awaiting: dict[str, dict[str, Any]] = {}

    def request(self, action_id: str, *, prompt: str) -> dict[str, Any]:
        entry = {"action_id": action_id, "prompt": prompt, "confirmed": False}
        self._awaiting[action_id] = entry
        return entry

    def confirm(self, action_id: str) -> bool:
        if action_id in self._awaiting:
            self._awaiting[action_id]["confirmed"] = True
            return True
        return False
