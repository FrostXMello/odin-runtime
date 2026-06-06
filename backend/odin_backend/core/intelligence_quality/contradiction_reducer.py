"""Reduce contradictory memory synthesis."""

from __future__ import annotations

from typing import Any


def reduce_contradictions(*, statements: list[str]) -> dict[str, Any]:
    normalized = [s.strip().lower() for s in statements if s.strip()]
    unique = list(dict.fromkeys(normalized))
    removed = len(normalized) - len(unique)
    pairs = 0
    for i, a in enumerate(unique):
        for b in unique[i + 1 :]:
            if a.startswith("not ") and b == a[4:] or b.startswith("not ") and a == b[4:]:
                pairs += 1
    resolved = max(0, len(unique) - pairs)
    return {"input": len(statements), "resolved": resolved, "contradictions": pairs, "removed_duplicates": removed}
