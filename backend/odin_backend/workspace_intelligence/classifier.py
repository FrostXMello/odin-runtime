"""Workspace session classification."""

import re
from enum import StrEnum


class WorkspaceSessionType(StrEnum):
    CODING = "coding"
    DEBUGGING = "debugging"
    DEPLOYMENT = "deployment"
    RESEARCH = "research"
    MONITORING = "monitoring"
    WRITING = "writing"
    GENERAL = "general"


class WorkspaceClassifier:
    def classify(
        self,
        *,
        apps: list[str] | None = None,
        window_titles: list[str] | None = None,
        terminal_output: str | None = None,
        browser_urls: list[str] | None = None,
    ) -> WorkspaceSessionType:
        blob = " ".join((apps or []) + (window_titles or []) + [terminal_output or ""] + (browser_urls or [])).lower()

        if re.search(r"\b(docker|kubectl|deploy|terraform|ansible)\b", blob):
            return WorkspaceSessionType.DEPLOYMENT
        if re.search(r"\b(debug|breakpoint|stack trace|exception|error)\b", blob):
            return WorkspaceSessionType.DEBUGGING
        if re.search(r"\b(grafana|dashboard|metrics|monitor|logs)\b", blob):
            return WorkspaceSessionType.MONITORING
        if re.search(r"\b(github|docs|research|stackoverflow|article)\b", blob):
            return WorkspaceSessionType.RESEARCH
        if re.search(r"\b(vscode|code|terminal|\.py|\.ts|git)\b", blob):
            return WorkspaceSessionType.CODING
        if re.search(r"\b(notion|write|markdown|doc)\b", blob):
            return WorkspaceSessionType.WRITING
        return WorkspaceSessionType.GENERAL
