"""Execution watchdog for supervised automation."""

from __future__ import annotations

from typing import Any


class ExecutionWatchdog:
    def __init__(self, app: Any) -> None:
        self._app = app

    def status(self) -> dict[str, Any]:
        runtime = getattr(self._app, "action_runtime", None)
        return {
            "emergency_stopped": runtime.emergency_stopped if runtime else False,
            "simulation_mode": getattr(self._app.settings, "automation_simulation_mode", True),
        }
