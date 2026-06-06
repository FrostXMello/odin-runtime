from __future__ import annotations
import time

def schedule(*, interval_s: float = 3600) -> dict:
    return {"interval_s": interval_s, "next_at": time.time() + interval_s}
