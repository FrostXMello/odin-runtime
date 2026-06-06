from __future__ import annotations
from typing import Any


def heatmap(layers: list[dict]) -> dict[str, Any]:
    cells = [round(float(l.get("weight", 0.1)) * 100) for l in layers]
    return {"cells": cells, "max": max(cells) if cells else 0}
