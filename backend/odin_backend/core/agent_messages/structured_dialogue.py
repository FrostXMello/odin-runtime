"""Structured dialogue message format."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def build_message(*, sender: str, kind: str, content: str, recipients: list[str]) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "sender": sender,
        "kind": kind,
        "content": content[:2000],
        "recipients": recipients,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
