from __future__ import annotations

from typing import Any


def build_semantic_map(*, files: list[str]) -> dict[str, Any]:
    modules = [f for f in files if f.endswith(".py")]
    return {"modules": len(modules), "symbols_estimated": len(modules) * 5}
