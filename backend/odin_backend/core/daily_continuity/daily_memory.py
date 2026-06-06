from __future__ import annotations
import time

def record(*, summary: str) -> dict:
    return {"summary": summary[:300], "day": time.strftime("%Y-%m-%d"), "ts": time.time()}
