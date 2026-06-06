from __future__ import annotations

from typing import Any


def sandbox_patch(*, diff: str) -> dict[str, Any]:
    return {"applied": True, "sandbox": True, "lines": len(diff.splitlines())}
