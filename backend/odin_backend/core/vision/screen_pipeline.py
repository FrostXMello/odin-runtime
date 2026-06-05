"""Screen understanding pipeline."""

from __future__ import annotations

from typing import Any

from odin_backend.core.vision.interaction_map import build_interaction_map
from odin_backend.core.vision.ocr_pipeline import run_ocr
from odin_backend.core.vision.scene_memory import SceneMemory
from odin_backend.core.vision.screen_capture import store_snapshot
from odin_backend.core.vision.ui_detection import detect_ui_elements
from odin_backend.core.vision.visual_parser import parse_scene


class ScreenUnderstandingPipeline:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._scenes = SceneMemory()
        self._screenshots: list[str] = []

    async def capture_and_parse(self, *, image_bytes: bytes | None = None) -> dict[str, Any]:
        path = store_snapshot(self._app.settings, image_bytes)
        self._screenshots.append(path)
        analysis = {}
        vision = getattr(self._app, "vision", None)
        if vision:
            try:
                a = await vision.analyze_screenshot(path)
                analysis = a.model_dump()
            except Exception:
                analysis = {}
        ocr = await run_ocr(self._app, path)
        ui = detect_ui_elements(ocr, analysis=analysis)
        scene = parse_scene(ocr_text=ocr, ui_elements=ui, path=path)
        scene["interaction_map"] = build_interaction_map(ui)
        scene["ocr_preview"] = ocr[:500]
        self._scenes.add(scene)
        if hasattr(self._app, "multimodal_perception"):
            await self._app.multimodal_perception.ingest_screenshot(path=path, analysis=scene)
        await self._ground_with_model(scene)
        return scene

    async def _ground_with_model(self, scene: dict[str, Any]) -> None:
        mgr = getattr(self._app, "model_manager", None)
        if not mgr:
            return
        try:
            summary = await mgr.runtime.infer(
                messages=[
                    {
                        "role": "user",
                        "content": f"Summarize this screen context locally:\n{scene.get('summary', '')}",
                    }
                ],
                task_kind="classification",
            )
            scene["model_summary"] = str(summary)[:400]
        except Exception:
            pass

    def list_screenshots(self) -> list[str]:
        return list(self._screenshots)[-20:]

    def snapshot(self) -> dict[str, Any]:
        return {"scenes": self._scenes.recent(), "screenshot_count": len(self._screenshots)}
