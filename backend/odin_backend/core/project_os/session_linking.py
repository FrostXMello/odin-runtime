"""Link coding sessions to projects."""

from __future__ import annotations

from typing import Any


class SessionLinking:
    def __init__(self) -> None:
        self._links: dict[str, str] = {}

    def link(self, session_id: str, project_id: str) -> None:
        self._links[session_id] = project_id

    def project_for(self, session_id: str) -> str | None:
        return self._links.get(session_id)
