from __future__ import annotations
from uuid import uuid4


def identity() -> dict:
    return {"assistant": "Odin", "simulated_emotion_disclosure": True, "identity_id": str(uuid4())}
