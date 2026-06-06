"""Performance GPU allocation."""

from __future__ import annotations


def allocate_vram(*, requested_mb: int, available_mb: int) -> dict[str, bool | int]:
    fits = requested_mb <= available_mb
    return {"fits": fits, "allocated_mb": min(requested_mb, available_mb) if fits else 0}
