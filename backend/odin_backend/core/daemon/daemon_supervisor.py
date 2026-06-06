"""Daemon supervision and modes."""

from __future__ import annotations

from typing import Any

MODES = ("desktop_assistant", "overnight_cognition", "passive_observer", "low_power")


def mode_config(mode: str) -> dict[str, Any]:
    configs = {
        "desktop_assistant": {"idle_compact": False, "cognition_depth": 2},
        "overnight_cognition": {"idle_compact": True, "cognition_depth": 1},
        "passive_observer": {"idle_compact": True, "cognition_depth": 0},
        "low_power": {"idle_compact": True, "cognition_depth": 0, "poll_s": 30},
    }
    return dict(configs.get(mode, configs["desktop_assistant"]))
