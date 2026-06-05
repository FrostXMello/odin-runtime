"""Rank sources by trust and relevance."""

from __future__ import annotations

from typing import Any


def rank_sources(sources: list[dict[str, Any]], *, topic: str = "") -> list[dict[str, Any]]:
    topic_l = topic.lower()

    def score(s: dict[str, Any]) -> float:
        trust = float(s.get("trust_score", 0.5))
        title = str(s.get("title", "")).lower()
        url = str(s.get("url", "")).lower()
        relevance = 0.2 if topic_l and topic_l in title + url else 0.0
        return trust + relevance

    return sorted(sources, key=score, reverse=True)
