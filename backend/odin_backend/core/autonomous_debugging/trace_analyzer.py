from __future__ import annotations


def analyze(trace: str) -> dict:
    lines = [l for l in trace.splitlines() if l.strip()]
    return {"frames": lines[:12], "error": lines[-1] if lines else ""}
