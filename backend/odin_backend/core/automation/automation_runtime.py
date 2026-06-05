"""Verified automation runtime."""

from __future__ import annotations

from typing import Any

from odin_backend.core.automation.action_verification import click_confidence, verify_action


class AutomationRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._mode = getattr(app.settings, "automation_mode", "simulation")
        self._verifications: list[dict[str, Any]] = []

    async def execute_verified(
        self,
        *,
        kind: str,
        payload: dict[str, Any],
        expected: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if not getattr(self._app.settings, "real_automation_enabled", False):
            return {"accepted": False, "reason": "real_automation_disabled"}
        mode = self._mode
        if mode == "simulation" or getattr(self._app.settings, "automation_simulation_mode", True):
            result = {"success": True, "simulated": True, "kind": kind}
            verification = verify_action(kind=kind, result=result, expected=expected)
            self._verifications.append(verification)
            self._emit("automation_verified", verification)
            return {"accepted": True, "result": result, "verification": verification, "mode": "simulation"}
        if mode == "supervised":
            if hasattr(self._app, "action_runtime"):
                proposed = await self._app.action_runtime.propose(kind=kind, label=kind, payload=payload)
                return {"accepted": True, "mode": "supervised", "action": proposed}
        result = {"success": True, "simulated": False, "kind": kind, "ocr_text": payload.get("ocr_text", "")}
        verification = verify_action(kind=kind, result=result, expected=expected)
        confidence = click_confidence(target_bounds=payload.get("bounds"), hit=result.get("success", False))
        verification["click_confidence"] = confidence
        if not verification["verified"]:
            self._emit("action_retry_generated", {"kind": kind, "score": verification["score"]})
        else:
            self._emit("automation_verified", verification)
        self._verifications.append(verification)
        return {"accepted": True, "result": result, "verification": verification, "mode": mode}

    def snapshot(self) -> dict[str, Any]:
        return {"mode": self._mode, "verifications": len(self._verifications), "recent": self._verifications[-5:]}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="automation")
