from __future__ import annotations

from typing import Any


def map_architecture(*, files: list[str]) -> dict[str, Any]:
    layers = {"api": 0, "core": 0, "tests": 0, "operator": 0}
    for f in files:
        fl = f.lower()
        if "api" in fl or "routes" in fl:
            layers["api"] += 1
        elif "core" in fl:
            layers["core"] += 1
        elif "test" in fl:
            layers["tests"] += 1
        elif "operator" in fl:
            layers["operator"] += 1
    dominant = max(layers, key=layers.get)
    return {"layers": layers, "dominant_layer": dominant}
