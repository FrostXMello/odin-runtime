"""Monitor configured local folders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


async def check_filesystem(app: Any) -> list[dict[str, Any]]:
    alerts: list[dict] = []
    watch_dirs = [
        getattr(app.settings, "sandbox_work_dir", None),
        getattr(app.settings, "chroma_persist_dir", None),
    ]
    for d in watch_dirs:
        if not d:
            continue
        path = Path(d)
        if not path.exists():
            alerts.append(
                {
                    "kind": "missing_path",
                    "severity": "low",
                    "message": f"Expected path missing: {path}",
                }
            )
    return alerts
