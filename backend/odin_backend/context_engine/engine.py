"""ContextEngine — situational awareness, snapshots, correlation."""

import json
from pathlib import Path
from typing import Any

from odin_backend.config import Settings
from odin_backend.context_engine.correlation import ContextCorrelator
from odin_backend.context_engine.sessions import (
    ApplicationContext,
    BrowserTabContext,
    ContextSnapshot,
    TerminalContext,
    UnifiedContextSession,
)
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ContextEngine:
    """Maintains environmental state when context awareness is opt-in."""

    def __init__(self, settings: Settings, event_bus: EventBus) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._correlator = ContextCorrelator()
        self._session: UnifiedContextSession | None = None
        self._snapshots: dict[str, ContextSnapshot] = {}
        self._store_path = Path("./data/context_engine.json")

    @property
    def enabled(self) -> bool:
        return self._settings.context_awareness_enabled

    async def set_enabled(self, enabled: bool) -> None:
        self._settings.context_awareness_enabled = enabled
        if not enabled:
            self._session = None

    def get_session(self) -> UnifiedContextSession | None:
        return self._session

    async def update_environment(
        self,
        *,
        application: str | None = None,
        window: str | None = None,
        tabs: list[dict[str, str]] | None = None,
        terminal_cwd: str | None = None,
        terminal_output: str | None = None,
        repository: str | None = None,
        workflow_id: str | None = None,
        conversation_id: str | None = None,
        project: str | None = None,
        interaction: str | None = None,
    ) -> UnifiedContextSession | None:
        if not self.enabled:
            return None

        apps: list[ApplicationContext] = []
        if application:
            apps = [ApplicationContext(name=application, window_title=window)]

        browser_tabs = [
            BrowserTabContext(url=t.get("url", ""), title=t.get("title", ""))
            for t in (tabs or [])
        ]

        terminals: list[TerminalContext] = []
        if terminal_cwd or terminal_output:
            terminals = [
                TerminalContext(
                    cwd=terminal_cwd,
                    recent_output_preview=(terminal_output or "")[:500],
                )
            ]

        wf_ids: list[str] = []
        if self._session and self._session.active_workflow_ids:
            wf_ids = list(self._session.active_workflow_ids)
        if workflow_id and workflow_id not in wf_ids:
            wf_ids.append(workflow_id)

        recent = list(self._session.recent_interactions[-20:]) if self._session else []
        if interaction:
            recent.append(interaction)

        self._session = self._correlator.correlate(
            applications=apps or (self._session.active_applications if self._session else []),
            tabs=browser_tabs or (self._session.browser_tabs if self._session else []),
            terminals=terminals or (self._session.terminals if self._session else []),
            workflow_ids=wf_ids,
            conversation_id=conversation_id
            or (self._session.conversation_session_id if self._session else None),
            project=project or (self._session.project if self._session else "PROJECT_ODIN"),
            repository=repository
            or (self._session.repository_path if self._session else None),
        )
        self._session.recent_interactions = recent
        self._persist()
        await self._emit()
        return self._session

    async def save_context_snapshot(self, label: str = "manual") -> ContextSnapshot:
        if not self._session:
            self._session = self._correlator.correlate()
        snap = ContextSnapshot(
            session_id=self._session.id,
            label=label,
            session_data=self._session.model_dump(mode="json"),
            summary=self.summarize_context_session(),
        )
        self._snapshots[snap.id] = snap
        return snap

    async def restore_context_snapshot(self, snapshot_id: str) -> UnifiedContextSession | None:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            return None
        self._session = UnifiedContextSession.model_validate(snap.session_data)
        await self._emit()
        return self._session

    def summarize_context_session(self) -> str:
        if not self._session:
            return "No active context session."
        return self._session.insight or f"Project: {self._session.project}"

    def list_snapshots(self) -> list[ContextSnapshot]:
        return sorted(self._snapshots.values(), key=lambda s: s.created_at, reverse=True)

    def explain_context(self) -> dict[str, Any]:
        """Explainable context for proactive systems."""
        if not self._session:
            return {"enabled": self.enabled, "active": False, "sources": []}
        sources = []
        if self._session.active_applications:
            sources.append("active_applications")
        if self._session.browser_tabs:
            sources.append("browser_tabs")
        if self._session.terminals:
            sources.append("terminals")
        if self._session.active_workflow_ids:
            sources.append("workflows")
        if self._session.conversation_session_id:
            sources.append("conversation")
        return {
            "enabled": self.enabled,
            "active": True,
            "insight": self._session.insight,
            "project": self._session.project,
            "sources": sources,
            "session_id": self._session.id,
        }

    def _persist(self) -> None:
        if not self._session:
            return
        try:
            self._store_path.parent.mkdir(parents=True, exist_ok=True)
            self._store_path.write_text(
                json.dumps(self._session.model_dump(mode="json"), indent=2)
            )
        except Exception as exc:
            logger.warning("context_engine_persist_failed", error=str(exc))

    def _load(self) -> None:
        if self._store_path.exists():
            try:
                data = json.loads(self._store_path.read_text())
                self._session = UnifiedContextSession.model_validate(data)
            except Exception as exc:
                logger.warning("context_engine_load_failed", error=str(exc))

    async def _emit(self) -> None:
        if not self._session:
            return
        await self._event_bus.publish(
            Event(
                type=EventType.CONTEXT_ENGINE_UPDATED,
                source=AgentId.ODIN,
                payload=self._session.model_dump(mode="json"),
            )
        )

    async def startup(self) -> None:
        self._load()
