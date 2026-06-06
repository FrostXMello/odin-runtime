from __future__ import annotations
import random

def run(*, baseline: float = 100.0) -> dict:
    score = baseline * random.uniform(0.92, 1.08)
    return {"score": round(score, 3), "baseline": baseline, "delta_pct": round((score - baseline) / baseline * 100, 2)}
