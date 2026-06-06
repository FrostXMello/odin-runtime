"""Daily workflow automation (Prompt 37)."""

from __future__ import annotations

from typing import Any


class DailyWorkflowRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app

    async def startup_routine(self) -> dict[str, Any]:
        if not getattr(self._app.settings, "daily_driver_enabled", False):
            return {"accepted": False, "reason": "daily_driver_disabled"}
        suggestions: list[str] = []
        if hasattr(self._app, "project_os") and self._app.project_os._registry.list_all():
            last = self._app.project_os._registry.list_all()[-1]
            suggestions.append(f"Resume {last.get('name', 'project')} work?")
        if hasattr(self._app, "self_healing"):
            snap = self._app.self_healing.snapshot()
            if snap.get("repairs", 0) > 0:
                suggestions.append(f"{snap['repairs']} repairs detected overnight.")
        briefing = None
        if hasattr(self._app, "communications_runtime"):
            briefing = await self._app.communications_runtime.briefing()
        if getattr(self._app.settings, "engineering_workspace_enabled", False):
            eng = await self.engineering_briefing()
            suggestions.extend(eng.get("suggestions", []))
        if getattr(self._app.settings, "cognitive_continuity_enabled", False) and hasattr(self._app, "cognitive_continuity"):
            restored = await self._app.cognitive_continuity.restore()
            unfinished = restored.get("restored", {}).get("unfinished", 0)
            if unfinished:
                suggestions.append(f"{unfinished} unfinished work items — restore continuity?")
        return {"accepted": True, "suggestions": suggestions, "briefing": briefing}

    async def engineering_briefing(self) -> dict[str, Any]:
        suggestions: list[str] = []
        if hasattr(self._app, "engineering_memory"):
            abandoned = self._app.engineering_memory._sessions.abandoned()
            if abandoned:
                suggestions.append(f"{len(abandoned)} debugging sessions abandoned recently.")
        if hasattr(self._app, "dev_workflows"):
            blocked = [i for i in getattr(self._app.dev_workflows._issues, "_issues", []) if i.get("blocked")]
            if blocked:
                suggestions.append(f"{len(blocked)} implementation tasks blocked.")
        if hasattr(self._app, "autonomous_debugging"):
            suggestions.append("Review open debugging cases in engineering console.")
        return {"suggestions": suggestions}

    async def idle_consolidation(self) -> dict[str, Any]:
        results: dict[str, Any] = {}
        if hasattr(self._app, "vector_memory"):
            results["memory"] = await self._app.vector_memory.consolidate()
        if hasattr(self._app, "storage_optimization"):
            results["storage"] = await self._app.storage_optimization.optimize()
        return {"accepted": True, "consolidated": results}

    def snapshot(self) -> dict[str, Any]:
        return {"enabled": getattr(self._app.settings, "daily_driver_enabled", False)}
