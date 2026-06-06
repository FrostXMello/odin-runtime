from __future__ import annotations

from typing import Any


def map_execution_flow(*, files: list[str]) -> dict[str, Any]:
    entry = next((f for f in files if "main" in f or "app.py" in f), files[0] if files else None)
    return {"entrypoint": entry, "depth": min(5, len(files))}
