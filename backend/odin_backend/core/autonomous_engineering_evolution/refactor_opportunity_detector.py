from __future__ import annotations


def detect(*, files: list[str]) -> list[str]:
    return [f for f in files if len(f) > 20][:3]
