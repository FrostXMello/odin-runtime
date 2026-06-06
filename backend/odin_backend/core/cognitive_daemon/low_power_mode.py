from __future__ import annotations


def transition(*, enabled: bool) -> dict:
    return {"low_power": enabled, "fps_cap": 8 if enabled else 30}
