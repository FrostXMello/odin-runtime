from __future__ import annotations
import time

def snapshot(*, uptime_s: float, idle: bool) -> dict:
    return {"uptime_s": uptime_s, "idle": idle, "ts": time.time()}
