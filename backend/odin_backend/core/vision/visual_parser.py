"""Semantic screen summary from OCR + UI."""

from __future__ import annotations

from typing import Any


def parse_scene(*, ocr_text: str, ui_elements: list[dict[str, Any]], path: str) -> dict[str, Any]:
    lower = ocr_text.lower()
    app_hint = "terminal" if "$" in ocr_text or "powershell" in lower else "application"
    return {
        "path": path,
        "app_hint": app_hint,
        "summary": ocr_text[:300] or f"Visual scene at {path}",
        "ui_count": len(ui_elements),
        "has_code": any(k in lower for k in ("def ", "function ", "class ", "import ")),
    }
