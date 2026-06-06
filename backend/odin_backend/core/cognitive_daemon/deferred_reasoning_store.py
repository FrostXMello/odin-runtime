from __future__ import annotations
import json
from pathlib import Path


def defer(*, path: str, thought: str) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    items = []
    if p.exists():
        items = json.loads(p.read_text(encoding="utf-8"))
    items.append(thought[:160])
    p.write_text(json.dumps(items[-32:]), encoding="utf-8")
    return {"deferred": True}


def restore(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False, "thoughts": []}
    return {"restored": True, "thoughts": json.loads(p.read_text(encoding="utf-8"))}
