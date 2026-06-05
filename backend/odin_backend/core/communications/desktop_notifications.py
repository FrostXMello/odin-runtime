"""Desktop notification stubs (local only)."""

from __future__ import annotations

from typing import Any


def format_notification(*, title: str, body: str) -> dict[str, Any]:
    return {"title": title, "body": body[:200], "delivered": False, "local_only": True}
