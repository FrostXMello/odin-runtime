"""UI element detection stub."""

from __future__ import annotations

from typing import Any


def detect_ui_elements(ocr_text: str, *, analysis: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    elements: list[dict] = []
    if analysis and analysis.get("ui_elements"):
        return list(analysis["ui_elements"])
    if "button" in ocr_text.lower():
        elements.append({"type": "button", "label": "detected", "confidence": 0.5})
    if "menu" in ocr_text.lower():
        elements.append({"type": "menu", "label": "menu", "confidence": 0.45})
    return elements
