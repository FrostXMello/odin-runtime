from __future__ import annotations

def repo(*, name: str, dirty: bool = False) -> dict:
    return {"name": name, "dirty": dirty}
