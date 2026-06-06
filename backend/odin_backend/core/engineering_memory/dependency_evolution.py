"""Dependency evolution tracking."""

from __future__ import annotations

from typing import Any


def track_dependency_change(*, repo: str, package: str, from_ver: str, to_ver: str) -> dict[str, Any]:
    return {
        "repo": repo,
        "package": package,
        "from": from_ver,
        "to": to_ver,
        "breaking": from_ver.split(".")[0] != to_ver.split(".")[0],
    }
