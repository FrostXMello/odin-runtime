"""Decompose research topics into sub-queries."""

from __future__ import annotations


def plan_research(topic: str) -> list[str]:
    base = topic.strip()
    if not base:
        return []
    return [
        f"What is {base}?",
        f"Recent developments in {base}",
        f"Key risks and contradictions about {base}",
        f"Actionable recommendations for {base}",
    ]
