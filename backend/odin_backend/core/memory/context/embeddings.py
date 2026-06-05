"""Lightweight embedding abstraction — token overlap similarity (no heavy infra)."""

from __future__ import annotations

import re
from typing import Iterable


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def similarity(a: str, b: str) -> float:
    ta, tb = tokenize(a), tokenize(b)
    if not ta or not tb:
        return 0.0
    inter = len(ta & tb)
    union = len(ta | tb)
    return inter / union if union else 0.0


def rank_by_similarity(query: str, items: Iterable[tuple[str, str]], *, limit: int = 5) -> list[tuple[str, float]]:
    scored = [(key, similarity(query, text)) for key, text in items]
    scored.sort(key=lambda x: -x[1])
    return [(k, s) for k, s in scored[:limit] if s > 0.1]
