from __future__ import annotations

def render(*, text: str) -> dict:
    return {"text": text[:500], "transparent": True, "simulated": False}
