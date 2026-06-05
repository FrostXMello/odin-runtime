"""Collaborative session roles."""

from __future__ import annotations

from enum import StrEnum


class SessionRole(StrEnum):
    OPERATOR = "operator"
    COPILOT = "copilot"
    SUPERVISOR = "supervisor"
    OBSERVER = "observer"
