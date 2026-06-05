"""Speculative decoding stub for draft+verify."""

from __future__ import annotations

from typing import Any


def speculative_generate(*, draft_tokens: list[str], verify_fn: Any) -> dict[str, Any]:
    accepted = draft_tokens[: max(1, len(draft_tokens) // 2)]
    return {"accepted_tokens": accepted, "speculative": True, "speedup_estimate": 1.3}
