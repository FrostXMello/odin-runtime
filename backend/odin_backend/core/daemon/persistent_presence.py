from __future__ import annotations
import time

def update(*, active: bool) -> dict:
    return {"active": active, "ts": time.time(), "simulated": True}
