from __future__ import annotations
import json
from pathlib import Path


def save_graph(*, path: str, graph: dict) -> dict:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(graph), encoding="utf-8")
    return {"saved": True}


def load_graph(*, path: str) -> dict:
    p = Path(path)
    if not p.exists():
        return {"restored": False}
    return {"restored": True, "graph": json.loads(p.read_text(encoding="utf-8"))}
