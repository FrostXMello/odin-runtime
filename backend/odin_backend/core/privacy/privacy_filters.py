"""Privacy filters for sensitive data."""

from __future__ import annotations

import re

SENSITIVE = re.compile(r"(api[_-]?key|password|secret|token)", re.I)


def filter_sensitive(text: str) -> tuple[str, bool]:
    if SENSITIVE.search(text):
        return "[REDACTED]", True
    return text, False
