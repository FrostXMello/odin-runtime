from __future__ import annotations


def loop(*, profile: str) -> dict:
    return {"profile": profile, "interval_s": 30 if profile == "balanced" else 60}
