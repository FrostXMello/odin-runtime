from __future__ import annotations


def patterns(*, switches: int) -> dict:
    return {"context_switches": switches, "deep_work": switches < 4}
