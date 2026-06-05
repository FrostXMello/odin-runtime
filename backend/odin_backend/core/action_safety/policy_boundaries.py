"""Policy boundaries for automation."""

from __future__ import annotations

from typing import Any

_PROTECTED_APPS = ("1password", "bitwarden", "keepass", "banking")


def check_policy(settings: Any, *, kind: str, payload: dict) -> tuple[bool, str]:
    if not getattr(settings, "action_engine_enabled", False):
        return False, "action_engine_disabled"
    app_name = str(payload.get("app", "")).lower()
    for protected in _PROTECTED_APPS:
        if protected in app_name:
            return False, f"protected_app:{protected}"
    if kind == "navigate" and str(payload.get("url", "")).startswith("file://"):
        return False, "filesystem_navigation_blocked"
    return True, "ok"
