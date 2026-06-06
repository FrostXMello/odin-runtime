"""Live personal operating layer."""
from __future__ import annotations
from typing import Any

from odin_backend.core.live_environment.adaptive_focus_detection import focus as detect_focus
from odin_backend.core.live_environment.environmental_context import context as env_context
from odin_backend.core.live_environment.interruption_classification import classify
from odin_backend.core.live_environment.operator_presence_tracking import track
from odin_backend.core.live_environment.realtime_context_fusion import fuse
from odin_backend.core.live_environment.workspace_attention_model import attention


class LiveEnvironmentRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._switches = 0

    async def update(self, *, duration_s: float = 60.0, reason: str = "") -> dict[str, Any]:
        if not getattr(self._app.settings, "live_environment_enabled", False):
            return {"accepted": False, "reason": "live_environment_disabled"}
        pres = track(active=True, duration_s=duration_s)
        foc = detect_focus(switches=self._switches, duration_s=duration_s)
        attn = attention(weight=0.8 if foc["focused"] else 0.4)
        env = env_context(
            on_battery=getattr(self._app.settings, "on_battery", False),
            heavy_load=getattr(self._app.settings, "heavy_load", False),
        )
        if reason:
            ic = classify(reason=reason)
            self._emit("interruption_classified", ic)
        self._emit("focus_state_changed", foc)
        self._emit("adaptive_presence_updated", pres)
        intensity = "low" if env["on_battery"] or env["heavy_load"] else "normal"
        return {"accepted": True, "presence": pres, "focus": foc, "attention": attn, "environment": env, "intensity": intensity, "fusion": fuse(signals=[reason] if reason else [])}

    async def record_switch(self) -> dict[str, Any]:
        self._switches += 1
        return {"accepted": True, "switches": self._switches}

    def snapshot(self) -> dict[str, Any]:
        return {"switches": self._switches}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_environment")
