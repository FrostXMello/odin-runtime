from __future__ import annotations

from typing import Any


def suggest_debug_steps(*, error: str, context: dict) -> dict[str, Any]:
    steps = ["Reproduce the error with minimal input", "Inspect recent changes", "Check logs and stack trace"]
    if "import" in error.lower():
        steps.insert(0, "Verify module path and dependencies")
    if context.get("test_failure"):
        steps.append("Run failing test in isolation")
    return {"error": error[:200], "steps": steps, "priority": "high" if "critical" in error.lower() else "medium"}
