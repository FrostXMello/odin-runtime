from __future__ import annotations
import json
import time
from pathlib import Path


def save_session(*, path: str, data: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({**data, "saved_at": time.time()}), encoding="utf-8")
    return {"saved": True}


def load_session(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "data": json.loads(p.read_text(encoding="utf-8"))}
