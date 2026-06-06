from __future__ import annotations

def assist(*, error: str) -> dict:
    hints = ["check stack trace", "run isolated tests", "inspect recent patches"]
    if "ImportError" in error:
        hints.insert(0, "verify module path")
    return {"error": error[:200], "hints": hints[:5], "supervised": True}
