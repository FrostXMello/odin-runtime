from __future__ import annotations

from typing import Any


def validate_diff(*, diff: str) -> dict[str, Any]:
    return {"valid": bool(diff.strip()) and not diff.startswith("--- /dev/null") or "+" in diff, "conflict_markers": "<<<<<<" in diff}
