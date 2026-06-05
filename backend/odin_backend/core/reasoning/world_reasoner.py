"""Planning-aware world reasoning."""

from __future__ import annotations

from typing import Any

from odin_backend.core.reasoning.causal_inference import infer_causal
from odin_backend.core.reasoning.hypothesis_engine import HypothesisEngine


class WorldReasoner:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._hypotheses = HypothesisEngine()

    def record_hypothesis(self, *, topic: str, hypothesis: str, confidence: float = 0.5) -> dict[str, Any]:
        return self._hypotheses.add(topic=topic, hypothesis=hypothesis, confidence=confidence)

    async def analyze(self, *, entity: str) -> dict[str, Any]:
        facts = []
        if hasattr(self._app, "knowledge_runtime"):
            facts = await self._app.knowledge_runtime.list_knowledge(entity=entity)
        causal = infer_causal(facts)
        uncertainty = 1.0 - (sum(f.get("confidence", 0.5) for f in facts) / max(len(facts), 1))
        return {
            "entity": entity,
            "fact_count": len(facts),
            "causal_links": causal,
            "uncertainty": round(uncertainty, 3),
            "hypotheses": self._hypotheses.list_all(),
        }

    def snapshot(self) -> dict[str, Any]:
        return {"hypotheses": self._hypotheses.list_all()}
