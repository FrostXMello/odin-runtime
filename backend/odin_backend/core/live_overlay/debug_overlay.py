from __future__ import annotations

def debug_panel(*, error: str) -> dict:
    return {"error": error[:200], "suggestions": ["check imports", "run tests"]}
