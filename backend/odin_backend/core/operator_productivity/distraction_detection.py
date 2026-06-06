from __future__ import annotations


def detect(*, context_switches: int) -> dict:
    return {"distracted": context_switches > 6, "switches": context_switches}
