from __future__ import annotations

def editor(*, file: str, line: int = 1) -> dict:
    return {"file": file, "line": line}
