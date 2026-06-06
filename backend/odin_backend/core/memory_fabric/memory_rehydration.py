from __future__ import annotations
import json
from pathlib import Path


def rehydrate(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "graph": json.loads(p.read_text(encoding="utf-8"))}
