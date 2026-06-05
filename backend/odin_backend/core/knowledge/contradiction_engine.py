"""Contradiction detection between knowledge items."""

from __future__ import annotations

from typing import Any


def detect_contradictions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    contradictions: list[dict] = []
    by_entity: dict[str, list[dict]] = {}
    for item in items:
        by_entity.setdefault(item.get("entity", ""), []).append(item)
    for entity, facts in by_entity.items():
        for i, a in enumerate(facts):
            for b in facts[i + 1 :]:
                if _conflicts(a.get("fact", ""), b.get("fact", "")):
                    contradictions.append(
                        {
                            "entity": entity,
                            "fact_a": a.get("fact"),
                            "fact_b": b.get("fact"),
                            "confidence_a": a.get("confidence"),
                            "confidence_b": b.get("confidence"),
                        }
                    )
    return contradictions


def _conflicts(a: str, b: str) -> bool:
    al, bl = a.lower(), b.lower()
    if not al or not bl or al == bl:
        return False
    neg_pairs = [("increase", "decrease"), ("true", "false"), ("yes", "no"), ("up", "down")]
    for x, y in neg_pairs:
        if x in al and y in bl:
            return True
        if y in al and x in bl:
            return True
    return False
