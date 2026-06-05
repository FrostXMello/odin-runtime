"""Revisit dormant objectives during idle."""

from __future__ import annotations

from typing import Any


def review_dormant(objectives: list[dict]) -> dict[str, Any]:
    dormant = [o for o in objectives if o.get("status") == "deferred"]
    return {"dormant_count": len(dormant), "revisited": min(len(dormant), 5)}
