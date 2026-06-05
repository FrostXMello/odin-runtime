"""Bounded crawl depth policy."""

from __future__ import annotations

from typing import Any


def allow_depth(settings: Any, depth: int) -> bool:
    return depth <= getattr(settings, "web_crawl_max_depth", 2)
