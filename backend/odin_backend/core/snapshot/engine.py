"""Global state snapshot engine."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SystemSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    label: str = "manual"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    kernel_state: dict[str, Any] = Field(default_factory=dict)
    context_graph: dict[str, Any] = Field(default_factory=dict)
    priority_queue: list[dict[str, Any]] = Field(default_factory=list)
    coherence_report: dict[str, Any] = Field(default_factory=dict)
    governor_decisions: list[dict[str, Any]] = Field(default_factory=list)
    autonomy_level: int = 1
    cognition_timeline: list[dict[str, Any]] = Field(default_factory=list)
    memory_delta_note: str = ""
    agent_profiles: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class SnapshotEngine:
    def __init__(self, store_dir: Path | None = None) -> None:
        self._dir = store_dir or Path("./data/snapshots")
        self._dir.mkdir(parents=True, exist_ok=True)
        self._snapshots: dict[str, SystemSnapshot] = {}

    def create_snapshot(self, app: Any, *, label: str = "manual") -> SystemSnapshot:
        snap = SystemSnapshot(
            label=label,
            kernel_state=app.kernel.get_state().model_dump(mode="json"),
            context_graph=app.context_graph.snapshot(),
            priority_queue=[i.model_dump() for i in app.priority_engine.rank(20)],
            coherence_report=app.coherence.last_report.model_dump(),
            governor_decisions=app.governor.recent_decisions(10),
            autonomy_level=app.autonomy.current_level,
            cognition_timeline=app.unified_cognition.timeline(15),
            memory_delta_note="Captured at snapshot time",
            agent_profiles=app.agent_society.list_profiles(),
            metadata={"odin_version": app.settings.app_version},
        )
        self._snapshots[snap.id] = snap
        path = self._dir / f"{snap.id}.json"
        path.write_text(json.dumps(snap.model_dump(mode="json"), indent=2, default=str))
        return snap

    def restore_snapshot(self, snapshot_id: str) -> SystemSnapshot | None:
        if snapshot_id in self._snapshots:
            return self._snapshots[snapshot_id]
        path = self._dir / f"{snapshot_id}.json"
        if path.exists():
            data = json.loads(path.read_text())
            snap = SystemSnapshot.model_validate(data)
            self._snapshots[snapshot_id] = snap
            return snap
        return None

    def diff_snapshots(self, a_id: str, b_id: str) -> dict[str, Any]:
        a = self.restore_snapshot(a_id)
        b = self.restore_snapshot(b_id)
        if not a or not b:
            return {"error": "Snapshot not found"}
        diffs: list[str] = []
        if a.kernel_state.get("current_focus") != b.kernel_state.get("current_focus"):
            diffs.append("current_focus changed")
        if a.coherence_report.get("coherence_score") != b.coherence_report.get("coherence_score"):
            diffs.append("coherence_score changed")
        if len(a.priority_queue) != len(b.priority_queue):
            diffs.append("priority_queue size changed")
        return {
            "from": a_id,
            "to": b_id,
            "differences": diffs,
            "focus_a": a.kernel_state.get("current_focus"),
            "focus_b": b.kernel_state.get("current_focus"),
        }

    def list_snapshots(self) -> list[SystemSnapshot]:
        for p in self._dir.glob("*.json"):
            sid = p.stem
            if sid not in self._snapshots:
                try:
                    self.restore_snapshot(sid)
                except Exception:
                    pass
        return sorted(self._snapshots.values(), key=lambda s: s.created_at, reverse=True)
