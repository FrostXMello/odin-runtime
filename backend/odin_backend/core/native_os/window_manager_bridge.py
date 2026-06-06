from __future__ import annotations
import platform


def snapshot(*, title: str = "unknown") -> dict:
    return {"platform": platform.system().lower(), "active_window": title[:120], "focused": True}
