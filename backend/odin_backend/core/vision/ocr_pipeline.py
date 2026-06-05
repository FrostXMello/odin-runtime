"""OCR pipeline — delegates to VisionService when available."""

from __future__ import annotations

from pathlib import Path
from typing import Any


async def run_ocr(app: Any, image_path: str) -> str:
    vision = getattr(app, "vision", None)
    if vision:
        analysis = await vision.analyze_screenshot(image_path)
        return analysis.ocr_text
    return _stub_ocr(image_path)


def _stub_ocr(path: str) -> str:
    p = Path(path)
    if p.exists() and p.stat().st_size > 0:
        return f"[ocr-stub] content from {p.name}"
    return ""
