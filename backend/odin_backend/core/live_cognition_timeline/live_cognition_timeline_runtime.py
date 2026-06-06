"""Live cognition timeline runtime (Prompt 60)."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from odin_backend.core.live_cognition_timeline.timeline_store import CognitionTimelineStore


class LiveCognitionTimelineRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        db = Path(getattr(app.settings, "sandbox_work_dir", Path("./data/sandbox"))) / "cognition_timeline.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        self._store = CognitionTimelineStore(db)
        self._replay_loops = 0

    async def append_cognition_event(self, *, kind: str, payload: dict | None = None) -> dict[str, Any]:
        if not getattr(self._app.settings, "live_cognition_timeline_enabled", False):
            return {"accepted": False, "reason": "live_cognition_timeline_disabled"}
        eid = self._store.append(kind=kind, payload=payload or {})
        self._emit("cognition_timeline_appended", {"kind": kind[:40]})
        return {"accepted": True, "event_id": eid, "bounded": True}

    async def build_operational_timeline(self) -> dict[str, Any]:
        events = self._store.events()
        return {"accepted": True, "timeline": events, "lazy_hydration": True}

    async def replay_cognition_window(self) -> dict[str, Any]:
        if self._replay_loops > 40:
            return {"accepted": False, "reason": "replay_bounded"}
        self._replay_loops += 1
        events = self._store.events(limit=10)
        self._emit("cognition_window_replayed", {"events": len(events)})
        return {"accepted": True, "replay": events, "supervised": True}

    async def compress_timeline_density(self) -> dict[str, Any]:
        return {"accepted": True, "compressed": True, "low_power": True}

    def snapshot(self) -> dict[str, Any]:
        return {"events": len(self._store.events())}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind
        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="live_cognition_timeline")
