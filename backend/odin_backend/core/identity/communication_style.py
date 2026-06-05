"""Communication tone preferences."""

from __future__ import annotations

from pydantic import BaseModel


class CommunicationStyle(BaseModel):
    tone: str = "professional"
    conciseness: float = 0.6
    explain_reasoning: bool = True
    use_technical_terms: bool = True
