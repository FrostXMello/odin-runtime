"""Semantic window / session classification."""

import re
from enum import StrEnum


class SessionType(StrEnum):
    DEVELOPMENT = "development"
    RESEARCH = "research"
    DEBUGGING = "debugging"
    WRITING = "writing"
    MONITORING = "monitoring"
    GENERAL = "general"


class SemanticClassifier:
    DEV_PATTERNS = re.compile(
        r"\b(vscode|code|terminal|git|docker|debug|\.py|\.ts|repo)\b", re.I
    )
    RESEARCH_PATTERNS = re.compile(
        r"\b(github|stackoverflow|docs|research|article|paper)\b", re.I
    )
    MONITOR_PATTERNS = re.compile(r"\b(dashboard|grafana|metrics|logs|monitor)\b", re.I)
    WRITE_PATTERNS = re.compile(r"\b(notion|docs|word|write|markdown)\b", re.I)

    def classify_window(self, title: str, app: str = "") -> SessionType:
        blob = f"{title} {app}".lower()
        if self.DEV_PATTERNS.search(blob):
            return SessionType.DEVELOPMENT
        if self.RESEARCH_PATTERNS.search(blob):
            return SessionType.RESEARCH
        if "debug" in blob or "error" in blob:
            return SessionType.DEBUGGING
        if self.MONITOR_PATTERNS.search(blob):
            return SessionType.MONITORING
        if self.WRITE_PATTERNS.search(blob):
            return SessionType.WRITING
        return SessionType.GENERAL

    def classify_session(self, windows: list[dict[str, str]]) -> SessionType:
        if not windows:
            return SessionType.GENERAL
        counts: dict[SessionType, int] = {}
        for w in windows:
            st = self.classify_window(w.get("title", ""), w.get("app", ""))
            counts[st] = counts.get(st, 0) + 1
        return max(counts, key=counts.get) if counts else SessionType.GENERAL
