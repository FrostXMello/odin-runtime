"""Mission deduplication and replay protection."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from odin_backend.models.mission import Mission, MissionLifecycle
from odin_backend.monitoring.logging import get_logger

logger = get_logger(__name__)

_NON_ALNUM = re.compile(r"[^a-z0-9\s]+")
_MULTI_SPACE = re.compile(r"\s+")


def normalize_objective(text: str) -> str:
    """Semantic normalization for duplicate detection."""
    t = text.strip().lower()
    t = _NON_ALNUM.sub(" ", t)
    t = _MULTI_SPACE.sub(" ", t).strip()
    return t


@dataclass(frozen=True)
class MissionFingerprint:
    normalized_objective: str
    mission_type: str
    originating_signal: str
    planning_context: str

    @property
    def digest(self) -> str:
        raw = "|".join(
            [
                self.normalized_objective,
                self.mission_type,
                self.originating_signal,
                self.planning_context,
            ]
        )
        return hashlib.sha256(raw.encode()).hexdigest()[:32]

    def to_dict(self) -> dict[str, str]:
        return {
            "normalized_objective": self.normalized_objective,
            "mission_type": self.mission_type,
            "originating_signal": self.originating_signal,
            "planning_context": self.planning_context,
            "digest": self.digest,
        }


def build_fingerprint(
    objective: str,
    *,
    mission_type: str = "standard",
    originating_signal: str = "api",
    planning_context: str = "",
) -> MissionFingerprint:
    return MissionFingerprint(
        normalized_objective=normalize_objective(objective),
        mission_type=mission_type.strip().lower() or "standard",
        originating_signal=originating_signal.strip().lower() or "api",
        planning_context=normalize_objective(planning_context) if planning_context else "",
    )


ACTIVE_BLOCKING = frozenset(
    {
        MissionLifecycle.QUEUED,
        MissionLifecycle.PLANNING,
        MissionLifecycle.PLANNED,
        MissionLifecycle.DISPATCHED,
        MissionLifecycle.RUNNING,
        MissionLifecycle.BLOCKED,
        MissionLifecycle.RETRYING,
        MissionLifecycle.ESCALATED,
        MissionLifecycle.APPROVAL_REQUIRED,
        # legacy mapped at runtime
        MissionLifecycle.ACTIVE,
        MissionLifecycle.WAITING,
    }
)


@dataclass
class DedupDecision:
    allow: bool
    reason: str = ""
    duplicate_mission_id: str | None = None
    action: str = "allow"  # allow | duplicate_active | replay_blocked | suppressed


class MissionDeduplicator:
    def __init__(self, *, replay_window_seconds: int = 3600) -> None:
        self._replay_window = replay_window_seconds
        self._suppressed_count = 0
        self._duplicate_count = 0
        self._replay_blocked_count = 0

    @property
    def metrics(self) -> dict[str, int]:
        return {
            "duplicate_suppressed_count": self._suppressed_count,
            "duplicate_detected_count": self._duplicate_count,
            "replay_blocked_count": self._replay_blocked_count,
        }

    def evaluate(
        self,
        fingerprint: MissionFingerprint,
        existing_missions: list[Mission],
    ) -> DedupDecision:
        now = datetime.now(timezone.utc)

        for mission in existing_missions:
            stored_fp = mission.metadata.get("fingerprint_digest")
            if not stored_fp:
                stored_norm = normalize_objective(mission.objective)
                if stored_norm != fingerprint.normalized_objective:
                    continue
            elif stored_fp != fingerprint.digest:
                continue

            state = _coerce_state(mission.current_state)
            if state in ACTIVE_BLOCKING or _is_legacy_active(state):
                self._duplicate_count += 1
                logger.warning(
                    "mission_duplicate_detected",
                    duplicate_of=mission.mission_id,
                    digest=fingerprint.digest,
                )
                return DedupDecision(
                    allow=False,
                    reason="identical active mission exists",
                    duplicate_mission_id=mission.mission_id,
                    action="duplicate_active",
                )

            if state == MissionLifecycle.COMPLETED:
                completed_at = _parse_ts(mission.metadata.get("completed_at"))
                if completed_at and (now - completed_at).total_seconds() < self._replay_window:
                    self._replay_blocked_count += 1
                    logger.warning(
                        "mission_replay_blocked",
                        prior=mission.mission_id,
                        digest=fingerprint.digest,
                        window_seconds=self._replay_window,
                    )
                    return DedupDecision(
                        allow=False,
                        reason="equivalent mission recently completed",
                        duplicate_mission_id=mission.mission_id,
                        action="replay_blocked",
                    )

        return DedupDecision(allow=True, action="allow")

    def record_suppressed(self) -> None:
        self._suppressed_count += 1
        logger.info("mission_suppressed", **self.metrics)


def _coerce_state(state: MissionLifecycle) -> MissionLifecycle:
    from odin_backend.core.missions.lifecycle import migrate_legacy_state

    return migrate_legacy_state(state)


def _is_legacy_active(state: MissionLifecycle) -> bool:
    return state in (MissionLifecycle.ACTIVE, MissionLifecycle.WAITING, MissionLifecycle.PLANNING)


def _parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
