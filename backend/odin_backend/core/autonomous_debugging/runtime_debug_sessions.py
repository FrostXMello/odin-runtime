from __future__ import annotations
from typing import Any
from uuid import uuid4


class RuntimeDebugSessions:
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def open(self) -> dict[str, Any]:
        sid = str(uuid4())
        self._sessions[sid] = {"id": sid}
        return self._sessions[sid]
