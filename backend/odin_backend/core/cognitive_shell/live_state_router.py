"""Route live state updates to subscribers."""

from __future__ import annotations

from typing import Any


def route_state(*, channel: str, payload: dict) -> dict[str, Any]:
    allowed = {
        "cognition-live:runtime",
        "thought-stream:runtime",
        "presence:runtime",
        "conversation:runtime",
    }
    if channel not in allowed:
        return {"accepted": False, "reason": "invalid_channel"}
    return {"accepted": True, "channel": channel, "payload_keys": list(payload.keys())}
