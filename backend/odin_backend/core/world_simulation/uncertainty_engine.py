"""Uncertainty quantification for simulations."""

from __future__ import annotations

from typing import Any


def quantify_uncertainty(*, confidence: float, evidence_count: int) -> dict[str, Any]:
    evidence_factor = min(1.0, evidence_count * 0.1)
    adjusted = confidence * (0.5 + 0.5 * evidence_factor)
    uncertainty = round(1.0 - adjusted, 4)
    return {"confidence": round(adjusted, 4), "uncertainty": uncertainty, "evidence_count": evidence_count}
