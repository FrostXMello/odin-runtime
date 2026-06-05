"""Record operator actions into reusable macros."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


class WorkflowRecorder:
    def __init__(self) -> None:
        self._recording = False
        self._session_id: str | None = None
        self._steps: list[dict[str, Any]] = []

    def start(self) -> dict[str, Any]:
        self._recording = True
        self._session_id = str(uuid4())
        self._steps = []
        return {"recording": True, "session_id": self._session_id}

    def record_step(self, action: dict[str, Any]) -> None:
        if self._recording:
            self._steps.append(
                {
                    "kind": action.get("kind"),
                    "label": action.get("label"),
                    "payload": action.get("payload", {}),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    def stop(self) -> dict[str, Any]:
        self._recording = False
        return {"session_id": self._session_id, "steps": list(self._steps), "step_count": len(self._steps)}

    @property
    def active(self) -> bool:
        return self._recording
