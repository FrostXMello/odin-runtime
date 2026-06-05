"""Federation mode policies."""

from __future__ import annotations

from typing import Any

MODES = ("isolated", "trusted_cluster", "supervised_mesh", "research_mesh")


class FederationPolicies:
    def __init__(self, settings: Any) -> None:
        self._settings = settings

    def allow_connect(self, mode: str) -> tuple[bool, str]:
        if not getattr(self._settings, "federation_enabled", False):
            return False, "federation_disabled"
        if mode not in MODES:
            return False, "invalid_mode"
        if mode == "isolated":
            return False, "isolated_mode"
        max_nodes = getattr(self._settings, "federation_max_nodes", 8)
        return True, "ok"

    def allow_remote_reasoning(self, mode: str) -> bool:
        return mode in ("trusted_cluster", "supervised_mesh", "research_mesh")

    def allow_knowledge_share(self, mode: str, trust: float) -> bool:
        min_trust = getattr(self._settings, "federation_min_trust_share", 0.4)
        return mode != "isolated" and trust >= min_trust
