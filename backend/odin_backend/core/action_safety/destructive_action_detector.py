"""Detect destructive automation patterns."""

from __future__ import annotations

_BLOCKED_KINDS = frozenset(
    {
        "delete_file",
        "format_disk",
        "shell_exec",
        "credential_harvest",
        "rm_rf",
        "registry_edit",
        "install_software",
    }
)


def is_destructive(kind: str, payload: dict) -> bool:
    if kind in _BLOCKED_KINDS:
        return True
    text = str(payload).lower()
    if "rm -rf" in text or "format c:" in text:
        return True
    return False
