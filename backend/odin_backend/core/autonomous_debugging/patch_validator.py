from __future__ import annotations

from typing import Any


def validate_patch(*, diff: str) -> dict[str, Any]:
    valid = bool(diff.strip()) and "<<<<<<" not in diff
    return {"valid": valid, "lines": len(diff.splitlines()), "conflicts": "<<<<<<" in diff}
