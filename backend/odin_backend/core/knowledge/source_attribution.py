"""Source lineage tracking."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def attribute_source(*, url: str, title: str = "", trust: float = 0.5) -> dict[str, Any]:
    return {
        "id": str(uuid4()),
        "url": url[:500],
        "title": title[:200],
        "trust_score": max(0.0, min(1.0, trust)),
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }
