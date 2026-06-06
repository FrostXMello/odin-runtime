from __future__ import annotations
from typing import Any


def prioritize(*, contexts: list[dict]) -> list[dict]:
    return sorted(contexts, key=lambda c: c.get("weight", 0), reverse=True)[:8]
