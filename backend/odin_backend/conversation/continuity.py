"""Objective continuity — active, paused, interrupted workflows."""

import re
from typing import Any

from odin_backend.conversation.sessions import ActiveObjective, ConversationSession

CANCEL_PATTERNS = re.compile(r"\b(cancel|stop|abort)\b.*\b(workflow|task|previous|that)\b", re.I)
CONTINUE_PATTERNS = re.compile(r"\b(continue|resume|pick up)\b.*\b(research|workflow|earlier|previous)\b", re.I)
COMPARE_PATTERNS = re.compile(r"\b(compare|contrast)\b.*\b(those|them|frameworks|options)\b", re.I)
SUMMARIZE_PATTERNS = re.compile(r"\b(summarize|recap|what we discussed)\b", re.I)


class ContinuityResolver:
    def resolve_intent(self, text: str, session: ConversationSession) -> dict[str, Any]:
        if CANCEL_PATTERNS.search(text):
            return {"action": "cancel_workflow", "target": self._latest_workflow(session)}
        if CONTINUE_PATTERNS.search(text):
            return {"action": "resume_objective", "target": self._latest_objective(session)}
        if COMPARE_PATTERNS.search(text):
            return {"action": "compare_context", "references": session.compressed_summary or self._recent_topics(session)}
        if SUMMARIZE_PATTERNS.search(text):
            return {"action": "summarize_conversation", "session_id": session.id}
        return {"action": "new_objective", "text": text}

    def _latest_workflow(self, session: ConversationSession) -> str | None:
        return session.linked_workflow_ids[-1] if session.linked_workflow_ids else None

    def _latest_objective(self, session: ConversationSession) -> ActiveObjective | None:
        active = [o for o in session.active_objectives if o.status in ("active", "paused")]
        return active[-1] if active else None

    def _recent_topics(self, session: ConversationSession) -> str:
        return " ".join(m.content[:100] for m in session.messages[-5:])
