"""SQLite-backed self-improvement memory."""
from __future__ import annotations

import time
from typing import Any

import aiosqlite

from odin_backend.core.self_improvement_memory.architecture_decisions import ArchitectureDecisions
from odin_backend.core.self_improvement_memory.failed_attempts import FailedAttempts
from odin_backend.core.self_improvement_memory.improvement_history import ImprovementHistory
from odin_backend.core.self_improvement_memory.optimization_knowledge import OptimizationKnowledge
from odin_backend.core.self_improvement_memory.patch_outcomes import PatchOutcomes
from odin_backend.core.self_improvement_memory.regression_memory import RegressionMemory


class SelfImprovementMemoryRuntime:
    def __init__(self, app: Any) -> None:
        self._app = app
        self._path = app.settings.database_url.replace("sqlite+aiosqlite:///", "")
        self._db: aiosqlite.Connection | None = None
        self._history: ImprovementHistory | None = None
        self._failed: FailedAttempts | None = None
        self._outcomes: PatchOutcomes | None = None
        self._knowledge: OptimizationKnowledge | None = None
        self._regressions: RegressionMemory | None = None
        self._decisions: ArchitectureDecisions | None = None

    async def _ensure(self) -> None:
        if self._db:
            return
        self._db = await aiosqlite.connect(self._path)
        self._history = ImprovementHistory(self._db)
        self._failed = FailedAttempts(self._db)
        self._outcomes = PatchOutcomes(self._db)
        self._knowledge = OptimizationKnowledge(self._db)
        self._regressions = RegressionMemory(self._db)
        self._decisions = ArchitectureDecisions(self._db)
        for store in (
            self._history,
            self._failed,
            self._outcomes,
            self._knowledge,
            self._regressions,
            self._decisions,
        ):
            await store.ensure()

    async def record_outcome(self, *, outcome: str, delta: float) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_improvement_memory_enabled", False):
            return {"accepted": False, "reason": "self_improvement_memory_disabled"}
        await self._ensure()
        entry = {"outcome": outcome, "delta": delta, "created_at": time.time()}
        assert self._history is not None
        await self._history.add(entry)
        if outcome == "failed":
            assert self._failed is not None
            await self._failed.record(entry)
        else:
            assert self._outcomes is not None
            await self._outcomes.record(entry)
        return {"accepted": True, "entry": entry}

    async def record_regression(self, *, metric: str, delta: float) -> dict[str, Any]:
        if not getattr(self._app.settings, "self_improvement_memory_enabled", False):
            return {"accepted": False, "reason": "self_improvement_memory_disabled"}
        await self._ensure()
        reg = {"metric": metric, "delta": delta}
        assert self._regressions is not None
        await self._regressions.record(reg)
        return {"accepted": True, "regression": reg}

    async def record_decision(self, *, title: str, rationale: str) -> dict[str, Any]:
        await self._ensure()
        d = {"title": title, "rationale": rationale, "created_at": time.time()}
        assert self._decisions is not None
        await self._decisions.record(d)
        return {"accepted": True, "decision": d}

    async def recent(self, limit: int = 20) -> list[dict]:
        if not getattr(self._app.settings, "self_improvement_memory_enabled", False):
            return []
        await self._ensure()
        assert self._history is not None
        return await self._history.recent(limit=limit)

    async def architecture_timeline(self) -> dict[str, Any]:
        await self._ensure()
        assert self._decisions is not None
        return {"accepted": True, "timeline": await self._decisions.timeline()}

    def snapshot(self) -> dict[str, Any]:
        return {"sqlite": True, "path": self._path}
