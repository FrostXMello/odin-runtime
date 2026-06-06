from __future__ import annotations

def schedule(*, idle: bool, survival_mode: str = "balanced") -> dict:
    interval = 30 if idle else 5
    if survival_mode == "overnight_daemon":
        interval = 120 if idle else 15
    return {"interval_s": interval, "bounded": True}
