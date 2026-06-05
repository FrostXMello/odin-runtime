"""Synthesize research reports."""

from __future__ import annotations

from typing import Any


async def synthesize(app: Any, *, topic: str, evidence: list[dict[str, Any]], contradictions: list[dict]) -> dict[str, Any]:
    snippets = [e.get("content", "")[:300] for e in evidence[:5]]
    summary = f"Research on '{topic}' from {len(evidence)} sources."
    if hasattr(app, "model_manager"):
        try:
            summary = str(
                await app.model_manager.runtime.infer(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Synthesize locally:\nTopic: {topic}\nEvidence:\n" + "\n".join(snippets),
                        }
                    ],
                    task_kind="synthesis",
                )
            )[:1500]
        except Exception:
            pass
    confidence = sum(float(e.get("trust_score", 0.5)) for e in evidence) / max(len(evidence), 1)
    return {
        "topic": topic,
        "summary": summary,
        "confidence": round(confidence, 3),
        "contradiction_count": len(contradictions),
        "follow_up_questions": [f"What changed recently in {topic}?", f"Who are key actors in {topic}?"],
    }
