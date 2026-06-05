"""Browser intelligence service — CDP + session awareness."""

from odin_backend.browser.cdp_client import CDPClient
from odin_backend.browser.session import (
    BrowserSession,
    BrowserTab,
    cluster_tabs,
    detect_research_topics,
    generate_session_insight,
)
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class BrowserIntelligenceService:
    def __init__(self, settings: Settings, event_bus: EventBus) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._cdp = CDPClient(settings.chrome_cdp_url)
        self._last_session: BrowserSession | None = None

    async def get_active_tabs(self) -> list[dict]:
        raw = await self._cdp.get_active_tabs()
        return raw

    async def analyze_session(self) -> BrowserSession:
        raw = await self._cdp.get_active_tabs()
        tabs = [BrowserTab(id=t.get("id"), title=t.get("title", ""), url=t.get("url", "")) for t in raw]
        clusters = cluster_tabs(tabs)
        topics = detect_research_topics(tabs)
        insight = generate_session_insight(tabs, topics)
        session = BrowserSession(tabs=tabs, clusters=clusters, insight=insight, research_topics=topics)
        self._last_session = session

        await self._event_bus.publish(
            Event(
                type=EventType.BROWSER_SESSION_UPDATED,
                source=AgentId.VALKYRIE,
                payload=session.model_dump(mode="json"),
            )
        )
        return session

    async def summarize_current_session(self) -> dict:
        session = await self.analyze_session()
        return {"insight": session.insight, "tab_count": len(session.tabs), "topics": session.research_topics}

    async def detect_research_cluster(self) -> dict:
        session = await self.analyze_session()
        return {"clusters": session.clusters, "topics": session.research_topics}

    def get_last_session(self) -> BrowserSession | None:
        return self._last_session
