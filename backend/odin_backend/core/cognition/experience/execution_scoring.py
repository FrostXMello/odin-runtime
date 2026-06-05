"""Execution fingerprint scoring."""

from __future__ import annotations

import hashlib
from typing import Any


def execution_fingerprint(
    *,
    capability: str,
    tool: str | None,
    mission_id: str,
    params_keys: list[str] | None = None,
) -> str:
    raw = f"{capability}|{tool or ''}|{mission_id}|{','.join(sorted(params_keys or []))}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def score_execution(*, success: bool, latency_ms: float | None, retries: int) -> float:
    base = 0.85 if success else 0.2
    if latency_ms and latency_ms > 60000:
        base -= 0.1
    base -= min(0.3, retries * 0.08)
    return max(0.05, min(0.99, base))
