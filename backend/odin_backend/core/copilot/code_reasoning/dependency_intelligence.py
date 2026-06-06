from __future__ import annotations

from typing import Any


def analyze_dependencies(*, files: list[str]) -> dict[str, Any]:
    imports = sum(1 for f in files if f.endswith(".py"))
    return {"estimated_modules": imports, "impact_radius": "low" if imports < 20 else "medium" if imports < 100 else "high"}
