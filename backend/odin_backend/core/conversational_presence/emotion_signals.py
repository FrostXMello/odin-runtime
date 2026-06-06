from __future__ import annotations


def emotion_from_energy(energy: float) -> dict:
    return {"valence": min(1.0, energy), "cadence": "steady" if energy < 0.7 else "animated"}
