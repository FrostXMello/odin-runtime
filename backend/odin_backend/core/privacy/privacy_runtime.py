"""Privacy runtime orchestrator."""

from __future__ import annotations

from typing import Any

from odin_backend.core.privacy.local_data_encryption import encrypt_local
from odin_backend.core.privacy.permission_audit import PermissionAudit
from odin_backend.core.privacy.privacy_filters import filter_sensitive
from odin_backend.core.privacy.runtime_permissions import check_permission
from odin_backend.core.privacy.secure_credentials import SecureCredentials


class PrivacyRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._vault = SecureCredentials()
        self._audit = PermissionAudit()

    async def filter_text(self, text: str) -> dict[str, Any]:
        if not getattr(self._app.settings, "privacy_enabled", False):
            return {"accepted": False, "reason": "privacy_disabled"}
        filtered, triggered = filter_sensitive(text)
        if triggered:
            self._emit("privacy_filter_triggered", {"redacted": True})
        return {"accepted": True, "text": filtered, "filtered": triggered}

    async def check(self, *, action: str, approved: bool = False) -> dict[str, Any]:
        allowed, reason = check_permission(action=action, approved=approved)
        self._audit.record(action=action, allowed=allowed, reason=reason)
        return {"allowed": allowed, "reason": reason}

    async def encrypt_snapshot(self, data: str) -> dict[str, Any]:
        enc = encrypt_local(data)
        return {"accepted": True, **enc}

    def snapshot(self) -> dict[str, Any]:
        return {"audit_entries": len(self._audit.recent(1000))}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="privacy")
