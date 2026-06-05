"""Risk classification for proposed actions."""

from __future__ import annotations

from typing import Any

from odin_backend.core.action_safety.destructive_action_detector import is_destructive
from odin_backend.core.action_safety.policy_boundaries import check_policy
from odin_backend.core.action_safety.sensitive_data_guard import contains_sensitive
from odin_backend.core.action_safety.rollback_guard import is_reversible


class ActionSafetyEngine:
    def __init__(self, app: Any) -> None:
        self._app = app

    def classify(self, *, kind: str, payload: dict[str, Any], hint: str | None = None) -> str:
        if is_destructive(kind, payload):
            return "blocked"
        if contains_sensitive(payload):
            return "restricted"
        allowed, _ = check_policy(self._app.settings, kind=kind, payload=payload)
        if not allowed:
            return "blocked"
        if hint == "blocked":
            return "blocked"
        if kind in ("shell_exec", "delete_file", "format_disk", "credential_harvest"):
            return "blocked"
        if kind.startswith("browser_") or kind == "navigate":
            return "supervised"
        if not is_reversible(kind):
            return "restricted"
        return hint or "supervised"
