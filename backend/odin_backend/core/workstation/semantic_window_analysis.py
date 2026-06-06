from __future__ import annotations

from typing import Any


def analyze_window(*, title: str, app: str) -> dict[str, Any]:
    coding = any(k in title.lower() for k in ("debug", "error", ".py", "odin"))
    return {"title": title[:80], "app": app, "coding_context": coding}
