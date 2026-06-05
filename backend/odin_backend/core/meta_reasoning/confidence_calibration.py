"""Confidence calibration measurement."""

from __future__ import annotations


def calibrate(*, predicted: float, actual: float) -> dict[str, float]:
    error = abs(predicted - actual)
    return {"calibration_error": round(error, 4), "well_calibrated": error < 0.2}
