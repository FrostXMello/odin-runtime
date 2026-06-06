"""Lazy loading policy."""

from __future__ import annotations


def should_lazy_load(*, component: str, idle: bool) -> bool:
    if idle and component in ("local_ai", "vector_memory", "embedding"):
        return True
    return False
