from __future__ import annotations
from typing import Any

def feedback(*, outcome: str, benchmark_delta: float) -> dict[str, Any]:
    improved = benchmark_delta > 0
    return {"outcome": outcome, "improved": improved, "delta": round(benchmark_delta, 4)}
