"""Research and knowledge quality (Prompt 38)."""

from __future__ import annotations

from typing import Any


def score_source(*, url: str, citations: int = 0) -> dict[str, Any]:
    trust = 0.5
    if url.endswith(".gov") or url.endswith(".edu"):
        trust = 0.85
    elif "github.com" in url:
        trust = 0.7
    trust = min(1.0, trust + citations * 0.02)
    return {"url": url, "trust": round(trust, 3)}


def validate_synthesis(*, claims: list[str], sources: list[str]) -> dict[str, Any]:
    ratio = len(sources) / max(len(claims), 1)
    valid = ratio >= 0.5
    return {"valid": valid, "source_ratio": round(ratio, 3)}


def decay_score(*, age_days: float) -> float:
    return round(max(0.1, 1.0 - age_days / 365), 3)


def track_topic(*, topic: str, updates: list[str]) -> dict[str, Any]:
    return {"topic": topic, "updates": len(updates), "active": len(updates) > 0}


def resolve_contradiction(*, a: str, b: str) -> dict[str, Any]:
    return {"resolved": a != b, "strategy": "prefer_recent" if len(a) >= len(b) else "prefer_specific"}


def citation_quality(*, citations: list[str]) -> dict[str, Any]:
    unique = len(set(citations))
    return {"count": len(citations), "unique": unique, "score": round(unique / max(len(citations), 1), 3)}


def long_horizon_plan(*, topic: str, horizon_days: int = 30) -> dict[str, Any]:
    return {"topic": topic, "horizon_days": horizon_days, "milestones": max(1, horizon_days // 7)}
