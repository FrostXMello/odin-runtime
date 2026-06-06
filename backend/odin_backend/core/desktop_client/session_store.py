from __future__ import annotations
import json
import time
from pathlib import Path

def save_session(*, path: str, data: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {**data, "saved_at": time.time()}
    p.write_text(json.dumps(payload), encoding="utf-8")
    return {"saved": True, "path": str(p)}

def load_session(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "data": json.loads(p.read_text(encoding="utf-8"))}
