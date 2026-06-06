from __future__ import annotations
from typing import Any


class FocusRecoveryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def recover(self, *, fatigue: bool = False) -> dict[str, Any]:
        if not getattr(self._app.settings, "predictive_focus_enabled", False):
            return {"accepted": False, "reason": "predictive_focus_disabled"}
        return {"accepted": True, "recovery_minutes": 15 if fatigue else 5, "operator_controlled": True}
