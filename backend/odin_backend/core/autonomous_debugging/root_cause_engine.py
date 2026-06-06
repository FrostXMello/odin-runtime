from __future__ import annotations

from typing import Any


def analyze_root_cause(*, error: str, location: str | None) -> dict[str, Any]:
    cause = "import_error" if "ImportError" in error else "runtime_error" if "Error" in error else "unknown"
    confidence = 0.8 if cause != "unknown" else 0.4
    return {"cause": cause, "location": location, "confidence": confidence}
