"""Select mentor agents by expertise."""

from __future__ import annotations

from typing import Any


def select_mentor(agents: list[dict[str, Any]], *, domain: str) -> dict[str, Any] | None:
    best = None
    best_score = -1.0
    for a in agents:
        domains = a.get("expertise_domains", [])
        conf = float(a.get("confidence", 0.5))
        score = conf + (0.2 if domain in domains else 0.0)
        if score > best_score:
            best_score = score
            best = a
    return best
