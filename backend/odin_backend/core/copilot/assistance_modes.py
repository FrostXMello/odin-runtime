"""Copilot assistance modes."""

from __future__ import annotations

from enum import StrEnum


class CopilotMode(StrEnum):
    PASSIVE_OBSERVER = "passive_observer"
    SUGGESTION = "suggestion"
    ACTIVE_COPILOT = "active_copilot"
    SUPERVISED_OPERATOR = "supervised_operator"
    AUTONOMOUS_ASSISTANT = "autonomous_assistant"
