"""Ensemble reasoning across fast + deep local models."""

from __future__ import annotations

from typing import Any


class EnsembleReasoner:
    def __init__(self, *, app: Any) -> None:
        self._app = app

    async def reason(
        self,
        *,
        prompt: str,
        mission_id: str | None = None,
    ) -> dict[str, Any]:
        mgr = self._app.model_manager
        selector = mgr.runtime.router
        fast = selector.select_model(
            capability=__import__(
                "odin_backend.core.models.model_profiles", fromlist=["ModelCapabilityTag"]
            ).ModelCapabilityTag.FAST,
            prefer_low_latency=True,
        )
        deep = selector.select_model(
            capability=__import__(
                "odin_backend.core.models.model_profiles", fromlist=["ModelCapabilityTag"]
            ).ModelCapabilityTag.REASONING,
        )
        messages = [{"role": "user", "content": prompt}]
        draft = await mgr.runtime.infer(messages=messages, model=fast, task_kind="routing", mission_id=mission_id)
        refined = await mgr.runtime.infer(
            messages=[
                {"role": "system", "content": "Refine the draft reasoning."},
                {"role": "user", "content": f"Draft:\n{draft}\n\nOriginal:\n{prompt}"},
            ],
            model=deep,
            task_kind="synthesis",
            mission_id=mission_id,
        )
        return {"draft": draft, "refined": refined, "models": {"fast": fast, "deep": deep}}
