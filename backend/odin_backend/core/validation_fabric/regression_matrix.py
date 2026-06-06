from __future__ import annotations

from typing import Any


def build_regression_matrix(*, before: str, after: str) -> dict[str, Any]:
    return {"cells": 4, "regressions": before != after, "coverage_delta": len(after) - len(before)}
