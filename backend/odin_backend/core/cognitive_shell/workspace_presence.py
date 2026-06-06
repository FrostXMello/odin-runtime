"""Workspace-aware presence."""

from __future__ import annotations

from typing import Any


def workspace_presence(*, app: str, title: str = "", debugging: bool = False) -> dict[str, Any]:
    label = "engineering" if debugging or "debug" in title.lower() else "general"
    return {"app": app, "title": title[:120], "context_label": label, "local_only": True}
