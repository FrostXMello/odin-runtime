"""Resolve contradictions from evidence."""

from __future__ import annotations

from typing import Any

from odin_backend.core.knowledge.contradiction_engine import detect_contradictions


def resolve_from_evidence(evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    facts = [
        {"entity": e.get("title", "source"), "fact": e.get("content", "")[:200], "confidence": e.get("trust_score", 0.5)}
        for e in evidence
    ]
    return detect_contradictions(facts)
