"""Production copilot runtime extending existing copilot."""

from __future__ import annotations

from typing import Any

from odin_backend.core.copilot.attention_model import AttentionModel
from odin_backend.core.copilot.contextual_help import generate_help
from odin_backend.core.copilot.operator_intent import detect_intent
from odin_backend.core.copilot.proactive_workspace_assistance import suggest
from odin_backend.core.copilot.realtime_assistant import assist
from odin_backend.core.copilot.ui_understanding import understand
from odin_backend.core.copilot.operator_workflow_profiles import OperatorWorkflowProfiles
from odin_backend.core.copilot.workspace_continuity import WorkspaceContinuity


class CopilotProductionRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._attention = AttentionModel()
        self._continuity = WorkspaceContinuity()
        self._profiles = OperatorWorkflowProfiles()
        self._actions: list[str] = []

    async def process_snapshot(self, snapshot: dict) -> dict[str, Any]:
        if not getattr(self._app.settings, "copilot_production_enabled", False):
            return {"accepted": False, "reason": "copilot_production_disabled"}
        ui = understand(snapshot)
        self._attention.update(app=ui["app"], duration_s=snapshot.get("focus_duration_s", 0))
        assistance = await assist(self._app, context=snapshot)
        intent = detect_intent(self._actions[-10:])
        profile = self._profiles.adapt(actions=self._actions)
        proactive = suggest(focus_app=ui["app"], patterns=self._actions)
        help_ctx = generate_help(app=ui["app"], task=intent.get("intent", "work"))
        ws_snap = self._continuity.capture(workspace=snapshot)
        return {
            "accepted": True,
            "ui": ui,
            "assistance": assistance,
            "intent": intent,
            "proactive": proactive,
            "help": help_ctx,
            "attention": self._attention.update(app=ui["app"], duration_s=snapshot.get("focus_duration_s", 0)),
            "workspace_snapshot_id": ws_snap["id"],
            "workflow_profile": profile,
        }

    async def resume_session(self) -> dict[str, Any]:
        restored = await self.restore_workspace()
        if hasattr(self._app, "project_os") and self._app.project_os._registry.list_all():
            pid = self._app.project_os._registry.list_all()[-1]["id"]
            proj = await self._app.project_os.restore(pid)
            restored["project"] = proj
        return {"accepted": True, "resume": "where_you_left_off", **restored}

    async def restore_workspace(self) -> dict[str, Any]:
        restored = self._continuity.restore_latest()
        if restored:
            self._emit("workspace_restored", {"snapshot_id": restored["id"]})
        return {"restored": restored is not None, "snapshot": restored}

    def record_action(self, action: str) -> None:
        self._actions.append(action)

    def snapshot(self) -> dict[str, Any]:
        base = {}
        if hasattr(self._app, "copilot_runtime"):
            base = self._app.copilot_runtime.snapshot()
        return {
            **base,
            "attention_app": self._attention._focus_app,
            "action_count": len(self._actions),
            "workspace_snapshots": len(self._continuity._snapshots),
            "workflow_profile": self._profiles._active,
        }

    def _emit(self, kind_name: str, payload: dict) -> None:
        obs = getattr(self._app, "observability", None)
        if not obs:
            return
        from odin_backend.core.observability.events import TraceEventKind

        try:
            kind = TraceEventKind(kind_name)
        except ValueError:
            return
        obs.tracer.record(kind, message=kind_name, payload=payload, component="copilot")
