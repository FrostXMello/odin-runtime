from __future__ import annotations
import json
import time
from pathlib import Path

def save_layout(*, path: str, layout: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {**layout, "saved_at": time.time()}
    p.write_text(json.dumps(payload), encoding="utf-8")
    return {"saved": True}

def load_layout(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False, "panels": []}
    data = json.loads(p.read_text(encoding="utf-8"))
    return {"restored": True, "layout": data}
