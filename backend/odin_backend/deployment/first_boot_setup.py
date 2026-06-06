"""First boot setup."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def first_boot_state(*, profile: str) -> dict[str, Any]:
    return {
        "first_boot": True,
        "profile": profile,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
