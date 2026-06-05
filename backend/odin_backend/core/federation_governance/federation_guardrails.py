"""Federation guardrails."""

from __future__ import annotations

from typing import Any


class FederationGuardrails:
    def __init__(self, settings: Any) -> None:
        self._settings = settings
        self._shutdown = False

    def is_shutdown(self) -> bool:
        return self._shutdown or not getattr(self._settings, "federation_enabled", False)

    def emergency_shutdown(self) -> dict[str, str]:
        self._shutdown = True
        return {"status": "federation_shutdown"}

    def allow_operation(self, op: str) -> tuple[bool, str]:
        if self._shutdown:
            return False, "federation_shutdown"
        if op == "internet_federation":
            return False, "internet_federation_blocked"
        return True, "ok"
