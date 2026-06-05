"""Replay recorded macros with supervision."""

from __future__ import annotations

from typing import Any

from odin_backend.core.workflow_macros.macro_learning import steps_to_macro
from odin_backend.core.workflow_macros.workflow_recorder import WorkflowRecorder


class MacroReplayEngine:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._recorder = WorkflowRecorder()

    async def start_recording(self) -> dict[str, Any]:
        result = self._recorder.start()
        self._emit("workflow_recorded", {"event": "recording_started"})
        return result

    async def stop_recording(self, *, name: str = "recorded_workflow") -> dict[str, Any]:
        recorded = self._recorder.stop()
        macro = steps_to_macro(recorded["steps"], name=name)
        if hasattr(self._app, "workflow_memory"):
            await self._app.workflow_memory.save(macro)
        self._emit("macro_generated", {"macro_id": macro["id"], "name": name})
        return {"macro": macro, **recorded}

    async def replay(self, macro: dict[str, Any], *, params: dict | None = None) -> list[dict[str, Any]]:
        results: list[dict] = []
        runtime = self._app.action_runtime
        for step in macro.get("steps", []):
            payload = dict(step.get("payload", {}))
            if params:
                for k, v in params.items():
                    if k in payload:
                        payload[k] = v
            proposed = await runtime.propose(
                kind=str(step.get("kind", "unknown")),
                label=str(step.get("label", "macro_step")),
                payload=payload,
            )
            if proposed["state"] == "blocked":
                results.append(proposed)
                break
            approved = await runtime.approve(proposed["id"])
            results.append(approved or proposed)
        return results

    def snapshot(self) -> dict[str, Any]:
        return {"recording": self._recorder.active}

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="macro_replay")
