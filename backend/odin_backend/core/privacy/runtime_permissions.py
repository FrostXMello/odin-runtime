"""Runtime permission checks."""

from __future__ import annotations


def check_permission(*, action: str, approved: bool = False) -> tuple[bool, str]:
    destructive = {"git_push", "delete_file", "send_email", "shell_exec"}
    if action in destructive and not approved:
        return False, "approval_required"
    return True, "allowed"
