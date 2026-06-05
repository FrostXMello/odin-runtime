"""Sensitive input masking."""

from __future__ import annotations

_SENSITIVE = ("password", "token", "secret", "api_key", "ssn", "credit_card")


def contains_sensitive(payload: dict) -> bool:
    text = str(payload).lower()
    return any(s in text for s in _SENSITIVE)
