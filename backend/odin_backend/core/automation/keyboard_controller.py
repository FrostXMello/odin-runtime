"""Keyboard control — simulation-first."""

from __future__ import annotations

from typing import Any


async def type_text(app: Any, *, text: str) -> dict[str, Any]:
    if getattr(app.settings, "automation_simulation_mode", True):
        return {"simulated": True, "action": "type", "length": len(text)}
    try:
        import pyautogui  # type: ignore

        pyautogui.write(text, interval=0.02)
        return {"executed": True, "length": len(text)}
    except Exception as exc:
        return {"simulated": True, "error": str(exc)}


async def key_press(app: Any, *, key: str) -> dict[str, Any]:
    if getattr(app.settings, "automation_simulation_mode", True):
        return {"simulated": True, "action": "key_press", "key": key}
    try:
        import pyautogui  # type: ignore

        pyautogui.press(key)
        return {"executed": True, "key": key}
    except Exception:
        return {"simulated": True, "key": key}
