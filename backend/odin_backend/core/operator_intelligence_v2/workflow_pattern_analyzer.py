from __future__ import annotations


def analyze(*, switches: int) -> dict:
    return {"switches": switches, "pattern": "deep_work" if switches < 5 else "fragmented"}
