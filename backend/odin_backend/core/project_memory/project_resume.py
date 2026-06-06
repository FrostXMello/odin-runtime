from __future__ import annotations
import json
from pathlib import Path


def save_resume(*, path: str, data: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data), encoding="utf-8")
    return {"saved": True}


def load_resume(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "data": json.loads(p.read_text(encoding="utf-8"))}
