"""Quick actions registry."""

from __future__ import annotations

from typing import Any

QUICK_ACTIONS = [
    {"id": "resume_session", "label": "Resume session"},
    {"id": "start_focus", "label": "Start focus block"},
    {"id": "run_briefing", "label": "Daily briefing"},
    {"id": "optimize_runtime", "label": "Optimize runtime"},
]


def list_actions() -> list[dict[str, Any]]:
    return list(QUICK_ACTIONS)
