"""Vision service — screenshots, OCR, UI semantics (no uncontrolled clicking)."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from odin_backend.events.bus import EventBus
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class VisionAnalysis(BaseModel):
    description: str = ""
    ocr_text: str = ""
    ui_elements: list[dict[str, Any]] = Field(default_factory=list)
    detected_windows: list[str] = Field(default_factory=list)
    charts_detected: bool = False
    terminal_detected: bool = False


class VisionService:
    """Interpret screenshots — no autonomous UI control."""

    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    async def analyze_screenshot(self, image_path: str | Path) -> VisionAnalysis:
        path = Path(image_path)
        analysis = VisionAnalysis(description=f"Screenshot at {path.name}")

        if not path.exists():
            analysis.description = "Screenshot file not found"
            return analysis

        try:
            from PIL import Image

            img = Image.open(path)
            analysis.description = f"Image {img.size[0]}x{img.size[1]} — visual interpretation stub"
            analysis.ui_elements = [
                {"type": "region", "label": "main_content", "confidence": 0.5},
            ]
        except ImportError:
            analysis.description = "PIL not installed — install pillow for image analysis"

        analysis.ocr_text = await self._ocr(path)
        analysis.terminal_detected = "terminal" in analysis.ocr_text.lower() or "$" in analysis.ocr_text
        analysis.charts_detected = any(w in analysis.ocr_text.lower() for w in ("chart", "graph", "%"))

        return analysis

    async def _ocr(self, path: Path) -> str:
        try:
            import pytesseract
            from PIL import Image

            return pytesseract.image_to_string(Image.open(path))[:10000]
        except Exception:
            return ""

    async def analyze_desktop_context(self, screenshot_paths: list[str]) -> dict:
        results = []
        for p in screenshot_paths[:3]:
            a = await self.analyze_screenshot(p)
            results.append(a.model_dump())
        return {"screenshots": results, "agent": str(AgentId.FREYA)}
