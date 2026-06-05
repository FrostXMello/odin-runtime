"""Mouse control — simulation-first with optional pyautogui."""

from __future__ import annotations

from typing import Any


async def mouse_click(app: Any, *, x: int, y: int, button: str = "left") -> dict[str, Any]:
    if getattr(app.settings, "automation_simulation_mode", True):
        return {"simulated": True, "action": "click", "x": x, "y": y, "button": button}
    try:
        import pyautogui  # type: ignore

        pyautogui.click(x, y, button=button)
        return {"executed": True, "x": x, "y": y}
    except Exception as exc:
        return {"simulated": True, "error": str(exc)}


async def mouse_move(app: Any, *, x: int, y: int) -> dict[str, Any]:
    if getattr(app.settings, "automation_simulation_mode", True):
        return {"simulated": True, "action": "move", "x": x, "y": y}
    try:
        import pyautogui  # type: ignore

        pyautogui.moveTo(x, y)
        return {"executed": True, "x": x, "y": y}
    except Exception:
        return {"simulated": True, "action": "move", "x": x, "y": y}
