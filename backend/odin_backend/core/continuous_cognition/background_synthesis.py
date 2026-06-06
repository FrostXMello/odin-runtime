from __future__ import annotations

from typing import Any


def synthesize_background(*, thoughts: list[str]) -> dict[str, Any]:
    return {"synthesized": len(thoughts), "summary": thoughts[-1][:80] if thoughts else ""}
