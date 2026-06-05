"""Research swarm agents."""

from __future__ import annotations

from typing import Any


class ScoutAgent:
    async def run(self, app: Any, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        return {"role": "scout", "findings": [e.get("url") for e in evidence[:3]], "topic": topic}


class VerifierAgent:
    async def run(self, app: Any, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        verified = sum(1 for e in evidence if e.get("status") in ("ok", "stub"))
        return {"role": "verifier", "verified_count": verified, "topic": topic}


class CriticAgent:
    async def run(self, app: Any, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        return {"role": "critic", "concerns": [f"Source trust low: {e.get('url')}" for e in evidence if e.get("trust_score", 1) < 0.5]}


class SynthesizerAgent:
    async def run(self, app: Any, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        return {"role": "synthesizer", "summary": f"Synthesis for {topic} across {len(evidence)} sources."}


class HistorianAgent:
    async def run(self, app: Any, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        hist = []
        if hasattr(app, "knowledge_runtime"):
            hist = app.knowledge_runtime._temporal.history(topic)
        return {"role": "historian", "history_length": len(hist)}


class StrategistAgent:
    async def run(self, app: Any, *, topic: str, evidence: list[dict]) -> dict[str, Any]:
        return {"role": "strategist", "recommendations": [f"Monitor {topic}", "Schedule follow-up research"]}
