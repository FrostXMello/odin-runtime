from __future__ import annotations

def reason(*, line: str) -> dict:
    return {"line": line[:200], "inference": "engineering session" if "pytest" in line else "general"}
