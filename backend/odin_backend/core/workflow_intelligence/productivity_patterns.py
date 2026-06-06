from __future__ import annotations

from typing import Any


def detect_patterns(*, history: list[str]) -> dict[str, Any]:
    debug = sum(1 for h in history if "debug" in h.lower())
    return {"debug_heavy": debug > 3, "samples": len(history)}
