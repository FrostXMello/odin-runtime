from __future__ import annotations

from typing import Any


def build_dependency_graph(*, files: list[str]) -> dict[str, Any]:
    return {"nodes": len(files), "edges": sum(1 for f in files if "import" in f or "__init__" in f)}
