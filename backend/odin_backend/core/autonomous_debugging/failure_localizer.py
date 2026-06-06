from __future__ import annotations

from typing import Any


def localize_failure(*, stacktrace: str, frames: list[str]) -> dict[str, Any]:
    file_line = frames[0] if frames else "unknown:0"
    return {"file": file_line, "confidence": 0.7 if frames else 0.3, "stacktrace_len": len(stacktrace)}
