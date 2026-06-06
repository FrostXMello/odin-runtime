from __future__ import annotations

from typing import Any


def reason_stacktrace(stacktrace: str) -> dict[str, Any]:
    lines = [l.strip() for l in stacktrace.splitlines() if l.strip()]
    frames = [l for l in lines if "File" in l or ".py" in l]
    error = lines[-1] if lines else "UnknownError"
    return {"error": error, "frames": frames, "depth": len(frames)}
