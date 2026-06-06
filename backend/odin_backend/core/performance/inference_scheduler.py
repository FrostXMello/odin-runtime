"""Inference scheduling."""

from __future__ import annotations


def schedule_inference(*, queue_depth: int, vram_pressure: str) -> dict[str, float | int]:
    max_concurrent = 2 if vram_pressure != "critical" else 1
    return {"max_concurrent": max_concurrent, "delay_ms": 0 if queue_depth < 3 else 100}
