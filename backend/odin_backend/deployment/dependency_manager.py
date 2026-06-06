"""Dependency checks."""

from __future__ import annotations

from typing import Any


REQUIRED = ("fastapi", "pydantic", "sqlalchemy")


def check_dependencies() -> dict[str, Any]:
    missing: list[str] = []
    for pkg in REQUIRED:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    return {"satisfied": len(missing) == 0, "missing": missing}
