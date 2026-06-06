from __future__ import annotations

from typing import Any


def suggest(*, context: dict) -> list[str]:
    hints = []
    if context.get("error"):
        hints.append("Inspect stack trace and recent commits")
    if context.get("repo"):
        hints.append(f"Review {context['repo']} architecture map")
    return hints or ["Continue current focus task"]
