"""Startup optimization."""

from __future__ import annotations

from typing import Any


def optimize_startup(*, components: list[str]) -> dict[str, Any]:
    deferred = [c for c in components if c not in ("config", "database", "observability")]
    return {"deferred": deferred, "eager": ["config", "database", "observability"]}
