from __future__ import annotations

from typing import Any


def proactive_hint(*, prediction: dict) -> str:
    return f"You usually continue {prediction.get('next', 'work')} next."
