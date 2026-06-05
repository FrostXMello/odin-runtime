"""UI element targeting from vision/OCR."""

from __future__ import annotations

from typing import Any


def locate_element(scene: dict[str, Any], *, label: str) -> dict[str, int] | None:
    for el in scene.get("ui_elements", []):
        if label.lower() in str(el.get("label", "")).lower():
            return {"x": int(el.get("x", 0)), "y": int(el.get("y", 0))}
    return None
