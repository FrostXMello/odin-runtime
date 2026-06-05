"""ConversationManager — persistent dialogue, objectives, interruptions."""

from datetime import datetime, timezone

from odin_backend.conversation.compression import compress_messages, summarize_for_continuity
from odin_backend.conversation.continuity import ContinuityResolver
from odin_backend.conversation.sessions import (
    ActiveObjective,
    ConversationMessage,
    ConversationSession,
    MessageRole,
)
from odin_backend.config import Settings
from odin_backend.events.bus import EventBus
from odin_backend.memory.coordinator import MimirCoordinator
from odin_backend.models.event import Event, EventType
from odin_backend.models.task import AgentId
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)


class ConversationManager:
    def __init__(
        self,
        settings: Settings,
        event_bus: EventBus,
        memory: MimirCoordinator,
    ) -> None:
        self._settings = settings
        self._event_bus = event_bus
        self._memory = memory
        self._sessions: dict[str, ConversationSession] = {}
        self._continuity = ContinuityResolver()

    def get_session(self, session_id: str) -> ConversationSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[ConversationSession]:
        return sorted(self._sessions.values(), key=lambda s: s.updated_at, reverse=True)

    async def start_session(self, title: str = "New conversation") -> ConversationSession:
        session = ConversationSession(title=title)
        self._sessions[session.id] = session
        await self._event_bus.publish(
            Event(
                type=EventType.CONVERSATION_STARTED,
                source=AgentId.ODIN,
                payload={"session_id": session.id, "title": title},
            )
        )
        return session

    async def add_message(
        self,
        session_id: str,
        role: MessageRole,
        content: str,
        *,
        metadata: dict | None = None,
    ) -> ConversationMessage:
        session = self._sessions[session_id]
        msg = ConversationMessage(role=role, content=content, metadata=metadata or {})
        session.messages.append(msg)
        session.updated_at = datetime.now(timezone.utc)

        if len(session.messages) > self._settings.conversation_max_turns:
            session.compressed_summary = summarize_for_continuity(session.messages)
            session.messages = session.messages[-self._settings.conversation_max_turns // 2 :]

        await self._memory.save_memory(
            f"[{role.value}] {content}",
            category="conversation",
            metadata={"session_id": session_id},
        )
        await self._event_bus.publish(
            Event(
                type=EventType.CONVERSATION_MESSAGE,
                source=AgentId.ODIN,
                correlation_id=session_id,
                payload=msg.model_dump(mode="json"),
            )
        )
        return msg

    async def process_user_turn(self, session_id: str, user_text: str) -> dict:
        """Resolve continuity intent and return structured handling hints for ODIN."""
        session = self._sessions[session_id]
        await self.add_message(session_id, MessageRole.USER, user_text)
        intent = self._continuity.resolve_intent(user_text, session)

        context_window = compress_messages(
            session.messages,
            max_chars=self._settings.conversation_context_token_budget,
        )
        memory_context = await self._memory.retrieve_related_context(user_text, limit=5)

        return {
            "session_id": session_id,
            "intent": intent,
            "context_window": context_window,
            "memory_context": memory_context,
            "compressed_summary": session.compressed_summary,
        }

    async def link_workflow(self, session_id: str, workflow_id: str, objective: str) -> None:
        session = self._sessions[session_id]
        if workflow_id not in session.linked_workflow_ids:
            session.linked_workflow_ids.append(workflow_id)
        obj = ActiveObjective(description=objective, workflow_id=workflow_id)
        session.active_objectives.append(obj)
        await self._event_bus.publish(
            Event(
                type=EventType.CONVERSATION_OBJECTIVE_UPDATED,
                source=AgentId.ODIN,
                payload={"session_id": session_id, "workflow_id": workflow_id},
            )
        )

    def get_context_for_reasoning(self, session_id: str) -> str:
        session = self._sessions[session_id]
        return compress_messages(session.messages)
