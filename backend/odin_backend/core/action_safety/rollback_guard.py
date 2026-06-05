"""Reversibility checks."""

from __future__ import annotations

_NON_REVERSIBLE = frozenset({"delete_file", "send_email", "submit_form", "shell_exec"})


def is_reversible(kind: str) -> bool:
    return kind not in _NON_REVERSIBLE
