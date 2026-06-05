"""PDF ingestion stub (local text extraction hook)."""

from __future__ import annotations

from typing import Any


def ingest_pdf(*, filename: str, text: str) -> dict[str, Any]:
    return {"filename": filename, "chars": len(text), "pages_estimated": max(1, len(text) // 3000)}
